from rest_framework.decorators import api_view
from rest_framework.response import Response
import structlog

logger = structlog.get_logger(__name__)


@api_view()
def home_api_view(request):
    logger.info("This is a rest-framework structured log")
    return Response({"message": "Hello, world!"})
