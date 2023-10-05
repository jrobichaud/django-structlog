from django.conf import settings

import structlog
from huey import crontab

logger = structlog.getLogger(__name__)


@settings.HUEY.task()
def huey_task():
    logger.info("huey task")


@settings.HUEY.periodic_task(crontab(minute="*/1"))
def huey_scheduled_task():
    logger.info("huey scheduled task")
