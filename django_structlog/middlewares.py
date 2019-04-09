import logging
import uuid

import structlog

logger = structlog.wrap_logger(logger=logging.getLogger(__name__))


class RequestLoggingMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_request(self, request):
        request.id = str(uuid.uuid4())
        logger.bind(request_id=request.id)
        logger.bind(user_id=request.user.id)

    def process_template_response(self, request, response):
        logger.info(
            'process_template_response',
            response_status_code=response.status_code,
            request=str(request),
            user_agent=request.META.get('HTTP_USER_AGENT'),
        )
        return response

    def process_exception(self, request, exception):
        logger.exception(
            'process_exception',
            exception,
        )
