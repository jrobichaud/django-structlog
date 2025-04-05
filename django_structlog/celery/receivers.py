import time
from typing import TYPE_CHECKING, Any, Optional, Type, cast

import structlog
from celery import current_app
from celery.signals import (
    after_task_publish,
    before_task_publish,
    task_failure,
    task_prerun,
    task_rejected,
    task_retry,
    task_revoked,
    task_success,
    task_unknown,
)

from . import signals

if TYPE_CHECKING:  # pragma: no cover
    from types import TracebackType

logger = structlog.getLogger(__name__)


class CeleryReceiver:
    _priority: Optional[str]

    def __init__(self) -> None:
        self._priority = None

    def receiver_before_task_publish(
        self,
        sender: Optional[Type[Any]] = None,
        headers: Optional[dict[str, Any]] = None,
        body: Optional[dict[str, str]] = None,
        properties: Optional[dict[str, Any]] = None,
        routing_key: Optional[str] = None,
        **kwargs: dict[str, str],
    ) -> None:
        if current_app.conf.task_protocol < 2:
            return

        context = structlog.contextvars.get_merged_contextvars(logger)
        if "task_id" in context:
            context["parent_task_id"] = context.pop("task_id")

        signals.modify_context_before_task_publish.send(
            sender=self.receiver_before_task_publish,
            context=context,
            task_routing_key=routing_key,
            task_properties=properties,
        )
        if properties:
            self._priority = properties.get("priority", None)
        cast(dict[str, Any], headers)["__django_structlog__"] = context

    def receiver_after_task_publish(
        self,
        sender: Optional[Type[Any]] = None,
        headers: Optional[dict[str, Optional[str]]] = None,
        body: Optional[dict[str, Optional[str]]] = None,
        routing_key: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        properties = {}
        if self._priority is not None:
            properties["priority"] = self._priority
            self._priority = None

        logger.info(
            "task_enqueued",
            child_task_id=(
                headers.get("id")
                if headers
                else cast(dict[str, Optional[str]], body).get("id")
            ),
            child_task_name=(
                headers.get("task")
                if headers
                else cast(dict[str, Optional[str]], body).get("task")
            ),
            routing_key=routing_key,
            **properties,
        )

    def receiver_task_prerun(
        self, task_id: str, task: Any, *args: Any, **kwargs: Any
    ) -> None:
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(task_id=task_id)
        metadata = getattr(task.request, "__django_structlog__", {})
        structlog.contextvars.bind_contextvars(**metadata)
        signals.bind_extra_task_metadata.send(
            sender=self.receiver_task_prerun, task=task, logger=logger
        )
        # Record the start time so we can log the task duration later.
        task.request._django_structlog_started_at = time.monotonic_ns()
        logger.info("task_started", task=task.name)

    def receiver_task_retry(
        self,
        request: Optional[Any] = None,
        reason: Optional[str] = None,
        einfo: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        logger.warning("task_retrying", reason=reason)

    def receiver_task_success(
        self, result: Optional[str] = None, sender: Optional[Any] = None, **kwargs: Any
    ) -> None:
        signals.pre_task_succeeded.send(
            sender=self.receiver_task_success, logger=logger, result=result
        )

        log_vars: dict[str, Any] = {}
        self.add_duration_ms(sender, log_vars)
        logger.info("task_succeeded", **log_vars)

    def receiver_task_failure(
        self,
        task_id: Optional[str] = None,
        exception: Optional[Exception] = None,
        traceback: Optional["TracebackType"] = None,
        einfo: Optional[Any] = None,
        sender: Optional[Type[Any]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        log_vars: dict[str, Any] = {}
        self.add_duration_ms(sender, log_vars)
        throws = getattr(sender, "throws", ())
        if isinstance(exception, throws):
            logger.info(
                "task_failed",
                error=str(exception),
                **log_vars,
            )
        else:
            logger.exception(
                "task_failed",
                error=str(exception),
                exception=exception,
                **log_vars,
            )

    @classmethod
    def add_duration_ms(
        cls, task: Optional[Type[Any]], log_vars: dict[str, Any]
    ) -> None:
        if task and hasattr(task, "_django_structlog_started_at"):
            started_at: int = task.request._django_structlog_started_at
            log_vars["duration_ms"] = round(
                (time.monotonic_ns() - started_at) / 1_000_000
            )

    def receiver_task_revoked(
        self,
        request: Any,
        terminated: Optional[bool] = None,
        signum: Optional[Any] = None,
        expired: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        metadata = getattr(request, "__django_structlog__", {}).copy()
        metadata["task_id"] = request.id
        metadata["task"] = request.task

        logger.warning(
            "task_revoked",
            terminated=terminated,
            signum=signum.value if signum is not None else None,
            signame=signum.name if signum is not None else None,
            expired=expired,
            **metadata,
        )

    def receiver_task_unknown(
        self,
        message: Optional[str] = None,
        exc: Optional[Exception] = None,
        name: Optional[str] = None,
        id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        logger.error(
            "task_not_found",
            task=name,
            task_id=id,
        )

    def receiver_task_rejected(
        self, message: Any, exc: Optional[Exception] = None, **kwargs: Any
    ) -> None:
        logger.exception(
            "task_rejected", task_id=message.properties.get("correlation_id")
        )

    def connect_signals(self) -> None:
        before_task_publish.connect(self.receiver_before_task_publish)
        after_task_publish.connect(self.receiver_after_task_publish)

    def connect_worker_signals(self) -> None:
        before_task_publish.connect(self.receiver_before_task_publish)
        after_task_publish.connect(self.receiver_after_task_publish)
        task_prerun.connect(self.receiver_task_prerun)
        task_retry.connect(self.receiver_task_retry)
        task_success.connect(self.receiver_task_success)
        task_failure.connect(self.receiver_task_failure)
        task_revoked.connect(self.receiver_task_revoked)
        task_unknown.connect(self.receiver_task_unknown)
        task_rejected.connect(self.receiver_task_rejected)
