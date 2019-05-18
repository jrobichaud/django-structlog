import logging
import os

import structlog
from celery import Celery, shared_task
from celery.signals import setup_logging
from django.apps import apps, AppConfig
from django.conf import settings

from django_structlog.celery.steps import DjangoStructLogInitStep

if not settings.configured:
    # set the default Django settings module for the 'celery' program.
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "config.settings.local"
    )  # pragma: no cover


app = Celery("django_structlog_demo_project")
# Using a string here means the worker will not have to
# pickle the object when using Windows.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# A step to initialize django-structlog
app.steps["worker"].add(DjangoStructLogInitStep)


@setup_logging.connect
def receiver_setup_logging(
    loglevel, logfile, format, colorize, **kwargs
):  # pragma: no cover
    logging.basicConfig(**settings.LOGGING)

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.ExceptionPrettyPrinter(),
            # structlog.processors.KeyValueRenderer(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


class CeleryAppConfig(AppConfig):
    name = "django_structlog_demo_project.taskapp"
    verbose_name = "Celery Config"

    def ready(self):
        installed_apps = [app_config.name for app_config in apps.get_app_configs()]
        app.autodiscover_tasks(lambda: installed_apps, force=True)


@app.task(bind=True)
def debug_task(self):
    print("Request: {request}".format(request=self.request))  # pragma: no cover


@shared_task
def successful_task(foo=None):
    import structlog

    logger = structlog.getLogger(__name__)
    logger.info("This is a successful task")


@shared_task
def failing_task(foo=None, **kwargs):
    raise Exception("This is a failed task")


@shared_task
def nesting_task():
    import structlog

    logger = structlog.getLogger(__name__)
    logger.bind(foo="Bar")
    logger.info("This is a nesting task")

    nested_task.delay()


@shared_task
def nested_task():
    import structlog

    logger = structlog.getLogger(__name__)
    logger.info("This is a nested task")
