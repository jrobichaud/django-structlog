import uuid

import structlog
from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils.decorators import sync_and_async_middleware
from asgiref import sync
from django.utils.deprecation import warn_about_renamed_method

from .. import signals

logger = structlog.getLogger(__name__)


def get_request_header(request, header_key, meta_key):
    if hasattr(request, "headers"):
        return request.headers.get(header_key)

    return request.META.get(meta_key)


class BaseRequestMiddleWare:
    def __init__(self, get_response):
        self.get_response = get_response

    def handle_response(self, request, response):
        if not hasattr(request, "_raised_exception"):
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

    @staticmethod
    def format_request(request):
        return "%s %s" % (request.method, request.get_full_path())

    def process_exception(self, request, exception):
        if isinstance(exception, (Http404, PermissionDenied)):
            # We don't log an exception here, and we don't set that we handled
            # an error as we want the standard `request_finished` log message
            # to be emitted.
            return

        setattr(request, "_raised_exception", exception)
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


class RequestMiddleware(BaseRequestMiddleWare):
    """``RequestMiddleware`` adds request metadata to ``structlog``'s logger context automatically.

    >>> MIDDLEWARE = [
        ...     # ...
        ...     'django_structlog.middlewares.RequestMiddleware',
        ... ]

    """

    sync_capable = True
    async_capable = True

    def __init__(self, get_response):
        super().__init__(get_response)
        if iscoroutinefunction(self.get_response):
            markcoroutinefunction(self)

    def __call__(self, request):
        if iscoroutinefunction(self):
            return self.__acall__(request)
        self.prepare(request)
        response = self.get_response(request)
        self.handle_response(request, response)
        return response

    async def __acall__(self, request):
        await sync.sync_to_async(self.prepare)(request)
        response = await self.get_response(request)
        await sync.sync_to_async(self.handle_response)(request, response)
        return response


@warn_about_renamed_method(
    class_name="django-structlog.middlewares",
    old_method_name="SyncRequestMiddleware",
    new_method_name="RequestMiddleware",
    deprecation_warning=DeprecationWarning,
)
class SyncRequestMiddleware(RequestMiddleware):
    pass


@warn_about_renamed_method(
    class_name="django-structlog.middlewares",
    old_method_name="AsyncRequestMiddleware",
    new_method_name="RequestMiddleware",
    deprecation_warning=DeprecationWarning,
)
class AsyncRequestMiddleware(RequestMiddleware):
    pass


@warn_about_renamed_method(
    class_name="django-structlog.middlewares",
    old_method_name="request_middleware_router",
    new_method_name="RequestMiddleware",
    deprecation_warning=DeprecationWarning,
)
@sync_and_async_middleware
def request_middleware_router(get_response):
    return RequestMiddleware(get_response)  # pragma: no cover
