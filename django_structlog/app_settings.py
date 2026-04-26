import logging

from django.conf import settings


# noinspection PyPep8Naming
class AppSettings:
    PREFIX = "DJANGO_STRUCTLOG_"

    @property
    def CELERY_ENABLED(self) -> bool:
        return getattr(settings, self.PREFIX + "CELERY_ENABLED", False)

    @property
    def CELERY_DEFAULT_LOG_LEVEL(self) -> int:
        return getattr(settings, self.PREFIX + "CELERY_DEFAULT_LOG_LEVEL", logging.INFO)

    @property
    def CELERY_TASK_START_LOG_LEVEL(self) -> int:
        return getattr(
            settings,
            self.PREFIX + "CELERY_TASK_START_LOG_LEVEL",
            self.CELERY_DEFAULT_LOG_LEVEL,
        )

    @property
    def CELERY_TASK_SUCCESS_LOG_LEVEL(self) -> int:
        return getattr(
            settings,
            self.PREFIX + "CELERY_TASK_SUCCESS_LOG_LEVEL",
            self.CELERY_DEFAULT_LOG_LEVEL,
        )

    @property
    def CELERY_TASK_NOTICE_LOG_LEVEL(self) -> int:
        return getattr(
            settings,
            self.PREFIX + "CELERY_TASK_RETRY_LOG_LEVEL",
            logging.WARNING,
        )

    @property
    def CELERY_TASK_FAILURE_LOG_LEVEL(self) -> int:
        return getattr(
            settings,
            self.PREFIX + "CELERY_TASK_FAILURE_LOG_LEVEL",
            logging.INFO,
        )

    @property
    def CELERY_TASK_ERROR_LOG_LEVEL(self) -> int:
        return getattr(
            settings,
            self.PREFIX + "CELERY_TASK_ERROR_LOG_LEVEL",
            logging.ERROR,
        )

    @property
    def IP_LOGGING_ENABLED(self) -> bool:
        return getattr(settings, self.PREFIX + "IP_LOGGING_ENABLED", True)

    @property
    def REQUEST_CANCELLED_LOG_LEVEL(self) -> int:
        return getattr(
            settings, self.PREFIX + "REQUEST_CANCELLED_LOG_LEVEL", logging.WARNING
        )

    @property
    def STATUS_DEFAULT_LOG_LEVEL(self) -> int:
        return getattr(settings, self.PREFIX + "STATUS_DEFAULT_LOG_LEVEL", logging.INFO)

    @property
    def STATUS_START_LOG_LEVEL(self) -> int:
        return getattr(
            settings,
            self.PREFIX + "STATUS_START_LOG_LEVEL",
            self.STATUS_DEFAULT_LOG_LEVEL,
        )

    @property
    def STATUS_2XX_LOG_LEVEL(self) -> int:
        return getattr(
            settings,
            self.PREFIX + "STATUS_2XX_LOG_LEVEL",
            self.STATUS_DEFAULT_LOG_LEVEL,
        )

    @property
    def STATUS_4XX_LOG_LEVEL(self) -> int:
        return getattr(settings, self.PREFIX + "STATUS_4XX_LOG_LEVEL", logging.WARNING)

    @property
    def STATUS_5XX_LOG_LEVEL(self) -> int:
        return getattr(settings, self.PREFIX + "STATUS_5XX_LOG_LEVEL", logging.ERROR)

    @property
    def COMMAND_LOGGING_ENABLED(self) -> bool:
        return getattr(settings, self.PREFIX + "COMMAND_LOGGING_ENABLED", False)

    @property
    def USER_ID_FIELD(self) -> str:
        return getattr(settings, self.PREFIX + "USER_ID_FIELD", "pk")


app_settings = AppSettings()
