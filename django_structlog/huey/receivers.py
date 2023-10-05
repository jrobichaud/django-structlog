from django.conf import settings
import structlog

from django_structlog.celery import signals

logger = structlog.getLogger(__name__)

STORAGE_KEY = "__django_structlog__"


def all_signal_handler(signal, task, exc=None):
    from huey import signals as S

    if signal == "enqueue":
        context = structlog.contextvars.get_merged_contextvars(logger)

        signals.modify_context_before_task_publish.send(
            sender=all_signal_handler, context=context
        )
        if "task_id" in context:
            context["parent_task_id"] = context.pop("task_id")

        # TODO: See https://github.com/coleifer/huey/issues/772
        task.kwargs[STORAGE_KEY] = context  # <- storage hack

        logger.info(
            "task_enqueued",
            child_task_id=task.id,
            child_task_name=task.name,
        )
    if signal == S.SIGNAL_EXECUTING:
        if STORAGE_KEY in task.kwargs:
            context = task.kwargs[STORAGE_KEY]  # <- storage hack
            del task.kwargs[STORAGE_KEY]  # <- storage hack

            structlog.contextvars.bind_contextvars(task_id=task.id)
            structlog.contextvars.bind_contextvars(**context)
            signals.bind_extra_task_metadata.send(
                sender=all_signal_handler, task=task, logger=logger
            )
            logger.info("task_started", task=task.name)


def connect_huey_signals():
    signal = settings.HUEY.signal
    signal()(all_signal_handler)
