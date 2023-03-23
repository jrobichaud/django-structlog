from asgiref.sync import iscoroutinefunction, markcoroutinefunction

from ..celery.receivers import receiver_before_task_publish, receiver_after_task_publish


class CeleryMiddleware:
    sync_capable = True
    async_capable = True
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
        from celery.signals import before_task_publish, after_task_publish

        before_task_publish.connect(receiver_before_task_publish)
        after_task_publish.connect(receiver_after_task_publish)
        if iscoroutinefunction(self.get_response):
            markcoroutinefunction(self)

    def __call__(self, request):
        if iscoroutinefunction(self):
            return self.__acall__(request)
        return self.get_response(request)

    async def __acall__(self, request):
        return await self.get_response(request)
