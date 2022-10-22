from django.apps import AppConfig


class UsersAppConfig(AppConfig):

    name = "django_structlog_demo_project.users"
    verbose_name = "Users"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        # noinspection PyUnresolvedReferences
        from . import signals  # noqa F401
