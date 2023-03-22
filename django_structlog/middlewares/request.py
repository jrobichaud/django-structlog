import asyncio
import uuid

import structlog
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils.decorators import sync_and_async_middleware
from asgiref import sync

from .. import signals

logger = structlog.getLogger(__name__)


def get_request_header(request, header_key, meta_key):
    if hasattr(request, "headers"):
        return request.headers.get(header_key)

    return request.META.get(meta_key)


class BaseRequestMiddleWare:
    def __init__(self, get_response):
        self.get_response = get_response
        self._raised_exception = False

    def handle_response(self, request, response):
        if not self._raised_exception:
            self.bind_user_id(request)
            signals.bind_extra_request_finished_metadata.send(
                sender=self.__class__,
                request=request,
                logger=logger,
                response=response,
            )
            logger.info(
                "request_finished",
                code=response.status_code,
                request=self.format_request(request),
            )
        structlog.contextvars.clear_contextvars()

    def prepare(self, request):
        from ipware import get_client_ip

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
        ip, _ = get_client_ip(request)
        structlog.contextvars.bind_contextvars(ip=ip)
        signals.bind_extra_request_metadata.send(
            sender=self.__class__, request=request, logger=logger
        )
        logger.info(
            "request_started",
            request=self.format_request(request),
            user_agent=request.META.get("HTTP_USER_AGENT"),
        )
        self._raised_exception = False

    @staticmethod
    def format_request(request):
        return "%s %s" % (request.method, request.get_full_path())

    def process_exception(self, request, exception):
        if isinstance(exception, (Http404, PermissionDenied)):
            # We don't log an exception here, and we don't set that we handled
            # an error as we want the standard `request_finished` log message
            # to be emitted.
            return

        self._raised_exception = True

        self.bind_user_id(request)
        signals.bind_extra_request_failed_metadata.send(
            sender=self.__class__,
            request=request,
            logger=logger,
            exception=exception,
        )
        logger.exception(
            "request_failed",
            code=500,
            request=self.format_request(request),
        )

    @staticmethod
    def bind_user_id(request):
        if hasattr(request, "user") and request.user is not None:
            user_id = None
            if hasattr(request.user, "pk"):
                user_id = request.user.pk
                if isinstance(user_id, uuid.UUID):
                    user_id = str(user_id)
            structlog.contextvars.bind_contextvars(user_id=user_id)


class SyncRequestMiddleware(BaseRequestMiddleWare):
    sync_capable = True
    async_capable = False

    def __call__(self, request):
        self.prepare(request)
        response = self.get_response(request)
        self.handle_response(request, response)
        return response


class AsyncRequestMiddleware(BaseRequestMiddleWare):
    sync_capable = False
    async_capable = True

    async def __call__(self, request):
        await sync.sync_to_async(self.prepare)(request)
        response = await self.delay_response(request)
        await sync.sync_to_async(self.handle_response)(request, response)
        return response

    async def delay_response(self, request):
        # acts as coroutine that doesn't block the event loop
        # (coroutine has been deprecated in Python 3.11)
        return await self.get_response(request)


class RequestMiddleware(SyncRequestMiddleware):
    """``RequestMiddleware`` adds request metadata to ``structlog``'s logger context automatically.

    >>> MIDDLEWARE = [
    ...     # ...
    ...     'django_structlog.middlewares.RequestMiddleware',
    ... ]

    """


@sync_and_async_middleware
def request_middleware_router(get_response):
    """``request_middleware_router`` select automatically between async or sync middleware.

    Use as a replacement for `django_structlog.middlewares.RequestMiddleware`

    >>> MIDDLEWARE = [
    ...     # ...
    ...     'django_structlog.middlewares.request_middleware_router',
    ... ]

    """
    if asyncio.iscoroutinefunction(get_response):
        return AsyncRequestMiddleware(get_response)
    return SyncRequestMiddleware(get_response)
