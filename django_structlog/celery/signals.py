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


modify_context_before_task_publish = django.dispatch.Signal(providing_args=["context"])
""" Signal to modify context passed over to ``celery`` task's context. You must modify the ``context`` dict.

>>> from django.dispatch import receiver
>>> from django_structlog.celery import signals
>>>
>>> @receiver(signals.modify_context_before_task_publish)
... def receiver_modify_context_before_task_publish(sender, signal, context):
...     keys_to_keep = {"request_id", "parent_task_id"}
...     new_dict = {
...         key_to_keep: context[key_to_keep]
...         for key_to_keep in keys_to_keep
...         if key_to_keep in context
...     }
...     context.clear()
...     context.update(new_dict)

"""
