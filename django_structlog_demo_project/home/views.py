import structlog
from django.http import HttpResponse
from django_structlog_demo_project.taskapp.celery import successful_task, failing_task

logger = structlog.get_logger(__name__)


def enqueue_successful_task(request):
    logger.info("Enqueuing successful task")
    successful_task.delay(foo='bar')
    return HttpResponse(status=201)


def enqueue_failing_task(request):
    logger.info("Enqueuing failing task")
    failing_task.delay(foo='bar')
    return HttpResponse(status=201)
