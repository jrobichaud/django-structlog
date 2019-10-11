from rest_framework.decorators import api_view as rest_api_view
from rest_framework.response import Response
import structlog

logger = structlog.get_logger(__name__)


@rest_api_view()
def api_view(request):
    logger.info("This is a rest-framework structured log")
    return Response({"message": "Hello, world!"})
