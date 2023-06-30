from django.conf import settings


# noinspection PyPep8Naming
class Settings:
    PREFIX = "DJANGO_STRUCTLOG_"

    @property
    def CELERY_ENABLED(self):
        return getattr(settings, self.PREFIX + "CELERY_ENABLED", False)


app_settings = Settings()
