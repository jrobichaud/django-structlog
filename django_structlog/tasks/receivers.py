from typing import TYPE_CHECKING, Any, Type

import django
import structlog
from django.core.cache import caches

from django_structlog.tasks import signals

logger = structlog.getLogger(__name__)

if TYPE_CHECKING:
    if django.VERSION >= (6, 0):
        from django.tasks.base import TaskResult  # type: ignore[import-untyped]
    else:
        TaskResult = Any


class BaseTaskReceiver:
    def get_task_context(self) -> dict[str, Any]:
        context = structlog.contextvars.get_merged_contextvars(logger)
        if "task_id" in context:
            context["parent_task_id"] = context.pop("task_id")
        return context

    def bind_context(self, context: dict[Any, Any] | Any) -> None:
        structlog.contextvars.bind_contextvars(**context)


class DjangoTaskReceiver(BaseTaskReceiver):

    def __init__(self) -> None:
        self.cache = caches["django_structlog"]

    def receiver_task_enqueued(
        self,
        sender: Type[Any],
        task_result: "TaskResult",
        **kwargs: dict[str, str],
    ) -> None:
        context = self.get_task_context()
        logger.info(
            "task_enqueued",
            task_id=task_result.id,
            task_name=task_result.task.module_path,
        )
        signals.modify_context_before_task_publish.send(
            sender=self.receiver_task_enqueued,
            context=context,
        )
        self.cache.set(task_result.id, context)

    def receiver_task_started(
        self,
        sender: Type[Any],
        task_result: "TaskResult",
        **kwargs: dict[str, str],
    ) -> None:
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(task_id=task_result.id)
        context = self.cache.get(task_result.id, default={})
        self.bind_context(context)
        signals.bind_extra_task_metadata.send(
            sender=self.receiver_task_started, task_result=task_result, logger=logger
        )
        logger.info(
            "task_started",
            task=task_result.task.module_path,
        )

    def receiver_task_finished(
        self,
        sender: Type[Any],
        task_result: "TaskResult",
        **kwargs: dict[str, str],
    ) -> None:
        from django.tasks.base import TaskResultStatus

        log_vars: dict[str, Any] = {}
        if task_result.status == TaskResultStatus.SUCCESSFUL:
            signals.pre_task_succeeded.send(
                sender=self.receiver_task_finished,
                logger=logger,
                task_result=task_result,
            )
            logger.info("task_succeeded", **log_vars)
        elif task_result.status == TaskResultStatus.FAILED:
            last_error = task_result.errors[-1]  # Get the last error
            if last_error:
                log_vars["exception_class"] = last_error.exception_class_path
                log_vars["traceback"] = last_error.traceback
            logger.error("task_failed", **log_vars)

    def connect_signals(self) -> None:
        if django.VERSION >= (6, 0):
            from django.tasks.signals import (  # type: ignore[import-untyped]
                task_enqueued,
                task_finished,
                task_started,
            )

            task_started.connect(self.receiver_task_started)
            task_finished.connect(self.receiver_task_finished)
            task_enqueued.connect(self.receiver_task_enqueued)
