import uuid

import structlog
import traceback
from .. import signals

logger = structlog.getLogger(__name__)


class RequestMiddleware(object):
    """ ``RequestMiddleware`` adds request metadata to ``structlog``'s logger context automatically.

    >>> MIDDLEWARE = [
    ...     # ...
    ...     'django_structlog.middlewares.RequestMiddleware',
    ... ]

    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from ipware import get_client_ip

        request_id = str(uuid.uuid4())
        with structlog.threadlocal.tmp_bind(logger):
            logger.bind(request_id=request_id)

            if hasattr(request, "user"):
                logger.bind(user_id=request.user.id)

            ip, routable = get_client_ip(request)
            logger.bind(ip=ip)
            signals.bind_extra_request_metadata.send(
                sender=self.__class__, request=request, logger=logger
            )

            logger.info(
                "request_started",
                request=request,
                user_agent=request.META.get("HTTP_USER_AGENT"),
            )
            try:
                response = self.get_response(request)

            except Exception as e:
                traceback_object = e.__traceback__
                formatted_traceback = traceback.format_tb(traceback_object)

                logger.error(
                    "request_failed",
                    error_message=str(e),
                    error_traceback=formatted_traceback,
                    code=500,
                    request=request,
                )
                raise
            else:
                logger.info(
                    "request_finished", code=response.status_code, request=request
                )

        return response
