from django.http import HttpResponse
from django_structlog_demo_project.taskapp.celery import successful_task, failing_task


def enqueue_successful_task(request):
    successful_task.delay(foo='bar')
    return HttpResponse(status=201)


def enqueue_failing_task(request):
    failing_task.delay(foo='bar')
    return HttpResponse(status=201)
