from celery import bootsteps

from .receivers import CeleryReceiver


class DjangoStructLogInitStep(bootsteps.Step):
    """``celery`` worker boot step to initialize ``django_structlog``.

    >>> from celery import Celery
    >>> from django_structlog.celery.steps import DjangoStructLogInitStep
    >>>
    >>> app = Celery("django_structlog_demo_project")
    >>> app.steps['worker'].add(DjangoStructLogInitStep)

    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.receiver = CeleryReceiver()
        self.receiver.connect_worker_signals()
