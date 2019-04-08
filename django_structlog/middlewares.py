import logging
import uuid

import structlog

logger = structlog.wrap_logger(logger=logging.getLogger(__name__))


class RequestLoggingMiddleware(object):

    def process_request(self, request):
        request.id = str(uuid.uuid4())
        logger.bind(request_id=request.id)
        logger.bind(user_id=request.user.id)

    def process_template_response(self, request, response):
        logger.info(
            'process_template_response',
            response_status_code=response.status_code,
            request=str(request),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        return response

    def process_exception(self, request, exception):
        logger.exception(
            'process_exception',
            exception
        )
