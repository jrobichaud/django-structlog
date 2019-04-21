from ..celery.receivers import receiver_before_task_publish, receiver_after_task_publish


class CeleryMiddleware(object):
    """
    ``CeleryMiddleware`` initializes ``celery`` signals to pass ``django``'s request information to ``celery`` worker's logger.

    >>> MIDDLEWARE = [
    ...     # ...
    ...     'django_structlog.middlewares.RequestMiddleware',
    ...     'django_structlog.middlewares.CeleryMiddleware',
    ... ]

    """
    def __init__(self, get_response=None):
        self.get_response = get_response
        from celery.signals import (
            before_task_publish,
            after_task_publish,
        )
        before_task_publish.connect(receiver_before_task_publish)
        after_task_publish.connect(receiver_after_task_publish)

    def __call__(self, request):
        return self.get_response(request)
