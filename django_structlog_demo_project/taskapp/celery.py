import logging
import logging.config
import os

import structlog
from celery import Celery, shared_task, signals
from django.apps import apps, AppConfig
from django.conf import settings

from django_structlog.celery.steps import DjangoStructLogInitStep

if not settings.configured:
    # set the default Django settings module for the 'celery' program.
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "config.settings.local"
    )  # pragma: no cover


app = Celery("django_structlog_demo_project", namespace="CELERY")

app.config_from_object("django.conf:settings")

# A step to initialize django-structlog
app.steps["worker"].add(DjangoStructLogInitStep)


@signals.setup_logging.connect
def receiver_setup_logging(
    loglevel, logfile, format, colorize, **kwargs
):  # pragma: no cover
    logging.config.dictConfig(settings.LOGGING)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            # structlog.processors.KeyValueRenderer(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
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
    logger = structlog.getLogger(__name__)
    structlog.contextvars.bind_contextvars(foo="Bar")
    logger.info("This is a nesting task")

    nested_task.delay()


@shared_task
def nested_task():
    logger = structlog.getLogger(__name__)
    logger.info("This is a nested task")
