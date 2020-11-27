import logging

import structlog
from django.http import HttpResponse
from django_structlog_demo_project.taskapp.celery import (
    successful_task,
    failing_task,
    nesting_task,
)

logger = structlog.get_logger(__name__)


def enqueue_successful_task(request):
    logger.info("Enqueuing successful task")
    successful_task.delay(foo="bar")
    return HttpResponse(status=201)


def enqueue_failing_task(request):
    logger.info("Enqueuing failing task")
    failing_task.delay(foo="bar")
    return HttpResponse(status=201)


def enqueue_nesting_task(request):
    logger.info("Enqueuing nesting task")
    nesting_task.delay()
    return HttpResponse(status=201)


def log_with_standard_logger(request):
    logging.getLogger("foreign_logger").info("This is a standard logger")
    return HttpResponse(status=200)


def raise_exception(request):
    raise Exception("This is a view raising an exception.")
