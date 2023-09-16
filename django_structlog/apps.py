from django.apps import AppConfig

from .app_settings import app_settings
from .commands import init_command_signals


class DjangoStructLogConfig(AppConfig):
    name = "django_structlog"

    def ready(self):
        if app_settings.CELERY_ENABLED:
            from .celery.receivers import connect_celery_signals

            connect_celery_signals()

        if app_settings.COMMAND_LOGGING_ENABLED:
            init_command_signals()
