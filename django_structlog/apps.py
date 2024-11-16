from django.apps import AppConfig

from .app_settings import app_settings


class DjangoStructLogConfig(AppConfig):
    name = "django_structlog"

    def ready(self) -> None:
        if app_settings.CELERY_ENABLED:
            from .celery.receivers import CeleryReceiver

            self._celery_receiver = CeleryReceiver()
            self._celery_receiver.connect_signals()

        if app_settings.COMMAND_LOGGING_ENABLED:
            from .commands import DjangoCommandReceiver

            self._django_command_receiver = DjangoCommandReceiver()
            self._django_command_receiver.connect_signals()
