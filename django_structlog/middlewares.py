import logging
import uuid

import structlog

logger = structlog.wrap_logger(logger=logging.getLogger(__name__))


class RequestLoggingMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = str(uuid.uuid4())
        with structlog.threadlocal.tmp_bind(logger):
            logger.bind(request_id=request_id)
            logger.bind(user_id=request.user.id)
            logger.info(
                'Request started',
                request=request,
                user_agent=request.META.get('HTTP_USER_AGENT'),
            )
            try:
                response = self.get_response(request)
            except Exception as e:
                logger.error(
                    'Request raised exception',
                    exception=str(e)
                )
            else:
                logger.info(
                    'Request finished',
                    response_status_code=response.status_code,
                )

        return response
