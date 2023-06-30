from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from django.utils.deprecation import warn_about_renamed_method

from .receivers import connect_celery_signals


@warn_about_renamed_method(
    class_name="django_structlog.middlewares",
    old_method_name="CeleryMiddleware",
    new_method_name="DJANGO_STRUCTLOG_CELERY_ENABLED = True",
    deprecation_warning=DeprecationWarning,
)
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

        connect_celery_signals()
        if iscoroutinefunction(self.get_response):
            markcoroutinefunction(self)

    def __call__(self, request):
        if iscoroutinefunction(self):
            return self.__acall__(request)
        return self.get_response(request)

    async def __acall__(self, request):
        return await self.get_response(request)
