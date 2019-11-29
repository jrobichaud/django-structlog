import uuid

import structlog
import traceback
from django.http import Http404

from .. import signals

logger = structlog.getLogger(__name__)


class RequestMiddleware:
    """ ``RequestMiddleware`` adds request metadata to ``structlog``'s logger context automatically.

    >>> MIDDLEWARE = [
    ...     # ...
    ...     'django_structlog.middlewares.RequestMiddleware',
    ... ]

    """

    def __init__(self, get_response):
        self.get_response = get_response
        self._raised_exception = False

    def __call__(self, request):
        from ipware import get_client_ip

        request_id = str(uuid.uuid4())
        with structlog.threadlocal.tmp_bind(logger):
            logger.bind(request_id=request_id)

            if hasattr(request, "user"):
                logger.bind(user_id=request.user.pk)

            ip, _ = get_client_ip(request)
            logger.bind(ip=ip)
            signals.bind_extra_request_metadata.send(
                sender=self.__class__, request=request, logger=logger
            )

            logger.info(
                "request_started",
                request=request,
                user_agent=request.META.get("HTTP_USER_AGENT"),
            )
            self._raised_exception = False
            response = self.get_response(request)
            if not self._raised_exception:
                logger.info(
                    "request_finished", code=response.status_code, request=request
                )

        return response

    def process_exception(self, request, exception):
        if isinstance(exception, Http404):
            # We don't log an exception here, and we don't set that we handled
            # an error as we want the standard `request_finished` log message
            # to be emitted.
            return

        self._raised_exception = True

        traceback_object = exception.__traceback__
        formatted_traceback = traceback.format_tb(traceback_object)
        logger.exception(
            "request_failed",
            code=500,
            request=request,
            error=exception,
            error_traceback=formatted_traceback,
        )
