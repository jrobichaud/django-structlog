import structlog
from ninja import NinjaAPI, Router
from ninja.security import SessionAuth

api = NinjaAPI(urls_namespace="ninja")
router = Router()

logger = structlog.get_logger(__name__)


# OptionalSessionAuth is a custom authentication class that allows the user to be anonymous
class OptionalSessionAuth(SessionAuth):
    def authenticate(self, request, key):
        return request.user


@router.get("/ninja", url_name="add", auth=OptionalSessionAuth())
def ninja(request):
    logger.info("This is a ninja structured log")
    return {"result": "ok"}


api.add_router("", router)
