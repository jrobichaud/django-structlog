import django.dispatch


bind_extra_task_metadata = django.dispatch.Signal(providing_args=["task", "logger"])
""" Signal to add extra ``structlog`` bindings from ``celery``'s task.

>>> from django.dispatch import receiver
>>> from django_structlog.celery import signals
>>> 
>>> @receiver(signals.bind_extra_task_metadata)
... def receiver_bind_extra_request_metadata(sender, signal, task=None, logger=None):
...     logger.bind(correlation_id=task.request.correlation_id)

"""
