from celery import bootsteps

from . import receivers


class DjangoStructLogInitStep(bootsteps.Step):
    """ ``celery`` worker boot step to initialize ``django_structlog``.

    >>> from celery import Celery
    >>> from django_structlog.celery.steps import DjangoStructLogInitStep
    >>>
    >>> app = Celery("django_structlog_demo_project")
    >>> app.steps['worker'].add(DjangoStructLogInitStep)

    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
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
        before_task_publish.connect(receivers.receiver_before_task_publish)
        after_task_publish.connect(receivers.receiver_after_task_publish)
        task_prerun.connect(receivers.receiver_task_pre_run)
        task_retry.connect(receivers.receiver_task_retry)
        task_success.connect(receivers.receiver_task_success)
        task_failure.connect(receivers.receiver_task_failure)
        task_revoked.connect(receivers.receiver_task_revoked)
        task_unknown.connect(receivers.receiver_task_unknown)
        task_rejected.connect(receivers.receiver_task_rejected)
