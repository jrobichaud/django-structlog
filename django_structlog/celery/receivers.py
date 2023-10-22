import structlog
from celery import current_app
from celery.signals import (
    before_task_publish,
    after_task_publish,
    task_prerun,
    task_retry,
    task_success,
    task_failure,
    task_revoked,
    task_unknown,
    task_rejected,
)

from . import signals


logger = structlog.getLogger(__name__)


class CeleryReceiver:
    def __init__(self):
        self._priority = None

    def receiver_before_task_publish(
        self,
        sender=None,
        headers=None,
        body=None,
        properties=None,
        routing_key=None,
        **kwargs,
    ):
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

        headers["__django_structlog__"] = context

    def receiver_after_task_publish(
        self, sender=None, headers=None, body=None, routing_key=None, **kwargs
    ):
        properties = {}
        if self._priority is not None:
            properties["priority"] = self._priority
            self._priority = None

        logger.info(
            "task_enqueued",
            child_task_id=headers.get("id") if headers else body.get("id"),
            child_task_name=headers.get("task") if headers else body.get("task"),
            routing_key=routing_key,
            **properties,
        )

    def receiver_task_prerun(self, task_id, task, *args, **kwargs):
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(task_id=task_id)
        metadata = getattr(task.request, "__django_structlog__", {})
        structlog.contextvars.bind_contextvars(**metadata)
        signals.bind_extra_task_metadata.send(
            sender=self.receiver_task_prerun, task=task, logger=logger
        )
        logger.info("task_started", task=task.name)

    def receiver_task_retry(self, request=None, reason=None, einfo=None, **kwargs):
        logger.warning("task_retrying", reason=reason)

    def receiver_task_success(self, result=None, **kwargs):
        signals.pre_task_succeeded.send(
            sender=self.receiver_task_success, logger=logger, result=result
        )
        logger.info("task_succeeded")

    def receiver_task_failure(
        self,
        task_id=None,
        exception=None,
        traceback=None,
        einfo=None,
        sender=None,
        *args,
        **kwargs,
    ):
        throws = getattr(sender, "throws", ())
        if isinstance(exception, throws):
            logger.info(
                "task_failed",
                error=str(exception),
            )
        else:
            logger.exception(
                "task_failed",
                error=str(exception),
                exception=exception,
            )

    def receiver_task_revoked(
        self, request=None, terminated=None, signum=None, expired=None, **kwargs
    ):
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
        self, message=None, exc=None, name=None, id=None, **kwargs
    ):
        logger.error(
            "task_not_found",
            task=name,
            task_id=id,
        )

    def receiver_task_rejected(self, message=None, exc=None, **kwargs):
        logger.exception(
            "task_rejected", task_id=message.properties.get("correlation_id")
        )

    def connect_signals(self):
        before_task_publish.connect(self.receiver_before_task_publish)
        after_task_publish.connect(self.receiver_after_task_publish)

    def connect_worker_signals(self):
        before_task_publish.connect(self.receiver_before_task_publish)
        after_task_publish.connect(self.receiver_after_task_publish)
        task_prerun.connect(self.receiver_task_prerun)
        task_retry.connect(self.receiver_task_retry)
        task_success.connect(self.receiver_task_success)
        task_failure.connect(self.receiver_task_failure)
        task_revoked.connect(self.receiver_task_revoked)
        task_unknown.connect(self.receiver_task_unknown)
        task_rejected.connect(self.receiver_task_rejected)
