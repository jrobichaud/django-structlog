import asyncio
import logging
import sys
import uuid
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    AsyncIterator,
    Awaitable,
    Callable,
    Generator,
    Iterator,
    Type,
    Union,
    cast,
)

import structlog
from asgiref import sync
from django.core.exceptions import PermissionDenied
from django.core.signals import got_request_exception
from django.http import Http404, StreamingHttpResponse
from django.utils.functional import SimpleLazyObject

from .. import signals
from ..app_settings import app_settings

if sys.version_info >= (3, 12, 0):
    from inspect import (  # type: ignore[attr-defined]
        iscoroutinefunction,
        markcoroutinefunction,
    )
else:
    from asgiref.sync import (  # type: ignore[no-redef]
        iscoroutinefunction,
        markcoroutinefunction,
    )

if TYPE_CHECKING:  # pragma: no cover
    from types import TracebackType

    from django.contrib.auth.base_user import AbstractBaseUser
    from django.http import HttpRequest, HttpResponse

logger = structlog.getLogger(__name__)


def get_request_header(request: "HttpRequest", header_key: str, meta_key: str) -> Any:
    if hasattr(request, "headers"):
        return request.headers.get(header_key)

    return request.META.get(meta_key)


def sync_streaming_content_wrapper(
    streaming_content: Iterator[bytes], context: Any
) -> Generator[bytes, None, None]:
    with structlog.contextvars.bound_contextvars(**context):
        logger.info("streaming_started")
        try:
            for chunk in streaming_content:
                yield chunk
        except Exception:
            logger.exception("streaming_failed")
            raise
        else:
            logger.info("streaming_finished")


async def async_streaming_content_wrapper(
    streaming_content: AsyncIterator[bytes], context: Any
) -> AsyncGenerator[bytes, Any]:
    with structlog.contextvars.bound_contextvars(**context):
        logger.info("streaming_started")
        try:
            async for chunk in streaming_content:
                yield chunk
        except asyncio.CancelledError:
            logger.warning("streaming_cancelled")
            raise
        except Exception:
            logger.exception("streaming_failed")
            raise
        else:
            logger.info("streaming_finished")


class RequestMiddleware:
    """``RequestMiddleware`` adds request metadata to ``structlog``'s logger context automatically.

    >>> MIDDLEWARE = [
    ...     # ...
    ...     'django_structlog.middlewares.RequestMiddleware',
    ... ]

    """

    sync_capable = True
    async_capable = True

    def __init__(
        self,
        get_response: Callable[
            ["HttpRequest"], Union["HttpResponse", Awaitable["HttpResponse"]]
        ],
    ) -> None:
        self.get_response = get_response
        if iscoroutinefunction(self.get_response):
            markcoroutinefunction(self)
        got_request_exception.connect(self.process_got_request_exception)

    def __call__(
        self, request: "HttpRequest"
    ) -> Union["HttpResponse", Awaitable["HttpResponse"]]:
        if iscoroutinefunction(self):
            return cast(RequestMiddleware, self).__acall__(request)
        self.prepare(request)
        response = cast("HttpResponse", self.get_response(request))
        self.handle_response(request, response)
        return response

    async def __acall__(self, request: "HttpRequest") -> "HttpResponse":
        await sync.sync_to_async(self.prepare)(request)
        try:
            response = await cast(Awaitable["HttpResponse"], self.get_response(request))
        except asyncio.CancelledError:
            logger.warning("request_cancelled")
            raise
        await sync.sync_to_async(self.handle_response)(request, response)
        return response

    def handle_response(self, request: "HttpRequest", response: "HttpResponse") -> None:
        if not hasattr(request, "_raised_exception"):
            self.bind_user_id(request)
            context = structlog.contextvars.get_merged_contextvars(logger)

            log_kwargs = dict(
                code=response.status_code,
                request=self.format_request(request),
            )
            signals.bind_extra_request_finished_metadata.send(
                sender=self.__class__,
                request=request,
                logger=logger,
                response=response,
                log_kwargs=log_kwargs,
            )
            if response.status_code >= 500:
                level = logging.ERROR
            elif response.status_code >= 400:
                level = app_settings.STATUS_4XX_LOG_LEVEL
            else:
                level = logging.INFO
            logger.log(
                level,
                "request_finished",
                **log_kwargs,
            )
            if isinstance(response, StreamingHttpResponse):
                streaming_content = response.streaming_content
                if response.is_async:
                    response.streaming_content = async_streaming_content_wrapper(
                        cast(AsyncIterator[bytes], streaming_content), context
                    )
                else:
                    response.streaming_content = sync_streaming_content_wrapper(
                        cast(Iterator[bytes], streaming_content), context
                    )

        else:
            exception = getattr(request, "_raised_exception")
            delattr(request, "_raised_exception")
            signals.update_failure_response.send(
                sender=self.__class__,
                request=request,
                response=response,
                logger=logger,
                exception=exception,
            )
        structlog.contextvars.clear_contextvars()

    def prepare(self, request: "HttpRequest") -> None:
        request_id = get_request_header(
            request, "x-request-id", "HTTP_X_REQUEST_ID"
        ) or str(uuid.uuid4())
        correlation_id = get_request_header(
            request, "x-correlation-id", "HTTP_X_CORRELATION_ID"
        )
        structlog.contextvars.bind_contextvars(request_id=request_id)
        self.bind_user_id(request)
        if correlation_id:
            structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
        if app_settings.IP_LOGGING_ENABLED:
            self.bind_ip(request)
        log_kwargs = {
            "request": self.format_request(request),
            "user_agent": request.META.get("HTTP_USER_AGENT"),
        }
        signals.bind_extra_request_metadata.send(
            sender=self.__class__, request=request, logger=logger, log_kwargs=log_kwargs
        )
        logger.info("request_started", **log_kwargs)

    @classmethod
    def bind_ip(cls, request: "HttpRequest") -> None:
        from ipware import get_client_ip  # type: ignore[import-untyped]

        ip, _ = get_client_ip(request)
        structlog.contextvars.bind_contextvars(ip=ip)

    @staticmethod
    def format_request(request: "HttpRequest") -> str:
        return f"{request.method} {request.get_full_path()}"

    @staticmethod
    def bind_user_id(request: "HttpRequest") -> None:
        user_id_field = app_settings.USER_ID_FIELD
        if not user_id_field or not hasattr(request, "user"):
            return

        session_was_accessed = (
            request.session.accessed if hasattr(request, "session") else None
        )

        if request.user is not None:
            user_id = None
            if hasattr(request.user, user_id_field):
                user_id = getattr(request.user, user_id_field)
                if isinstance(user_id, uuid.UUID):
                    user_id = str(user_id)
            structlog.contextvars.bind_contextvars(user_id=user_id)

        if session_was_accessed is False:
            """using SessionMiddleware but user was never accessed, must reset accessed state"""
            user = request.user

            def get_user() -> Any:
                request.session.accessed = True
                return user

            request.user = cast("AbstractBaseUser", SimpleLazyObject(get_user))
            request.session.accessed = False

    def process_got_request_exception(
        self, sender: Type[Any], request: "HttpRequest", **kwargs: Any
    ) -> None:
        if not hasattr(request, "_raised_exception"):
            ex = cast(
                tuple[Type[Exception], Exception, "TracebackType"],
                sys.exc_info(),
            )
            self._process_exception(request, ex[1])

    def _process_exception(self, request: "HttpRequest", exception: Exception) -> None:
        if isinstance(exception, (Http404, PermissionDenied)):
            # We don't log an exception here, and we don't set that we handled
            # an error as we want the standard `request_finished` log message
            # to be emitted.
            return

        setattr(request, "_raised_exception", exception)
        self.bind_user_id(request)
        log_kwargs = dict(
            code=500,
            request=self.format_request(request),
        )
        signals.bind_extra_request_failed_metadata.send(
            sender=self.__class__,
            request=request,
            logger=logger,
            exception=exception,
            log_kwargs=log_kwargs,
        )
        logger.exception(
            "request_failed",
            **log_kwargs,
        )
