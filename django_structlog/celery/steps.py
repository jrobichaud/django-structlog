from celery import bootsteps

from . import receivers


class DjangoStructLogInitStep(bootsteps.Step):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        from celery.signals import (
            task_prerun,
            task_retry,
            task_success,
            task_failure,
            task_revoked,
            task_unknown,
            task_rejected,
        )
        task_prerun.connect(receivers.receiver_task_pre_run)
        task_retry.connect(receivers.receiver_task_retry)
        task_success.connect(receivers.receiver_task_success)
        task_failure.connect(receivers.receiver_task_failure)
        task_revoked.connect(receivers.receiver_task_revoked)
        task_unknown.connect(receivers.receiver_task_unknown)
        task_rejected.connect(receivers.receiver_task_rejected)
