import structlog
from django.tasks import task

logger = structlog.getLogger(__name__)


@task
def django_task():
    logger.info("This is a Django 6 native task using the built-in task framework")

    return "ok"


@task
def django_failing_task():
    logger.info("This is a failing Django 6 native task")

    raise ValueError("Intentional failure in Django task")
