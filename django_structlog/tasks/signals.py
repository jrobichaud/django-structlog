import django.dispatch

bind_extra_task_metadata = django.dispatch.Signal()
""" Signal to add extra ``structlog`` bindings from ``celery``'s task.

:param task: the celery task being run
:param logger: the logger to bind more metadata or override existing bound metadata

>>> from django.dispatch import receiver
>>> from django_structlog.celery import signals
>>> import structlog
>>>
>>> @receiver(signals.bind_extra_task_metadata)
... def receiver_bind_extra_task_metadata(sender, signal, task=None, logger=None, **kwargs):
...     structlog.contextvars.bind_contextvars(correlation_id=task.request.correlation_id)

"""


modify_context_before_task_publish = django.dispatch.Signal()
""" Signal to modify context passed over to ``celery`` task's context. You must modify the ``context`` dict.

:param context: the context dict that will be passed over to the task runner's logger
:param task_routing_key: routing key of the task
:param task_properties: task's message properties

>>> from django.dispatch import receiver
>>> from django_structlog.celery import signals
>>>
>>> @receiver(signals.modify_context_before_task_publish)
... def receiver_modify_context_before_task_publish(sender, signal, context, task_routing_key=None, task_properties=None, **kwargs):
...     keys_to_keep = {"request_id", "parent_task_id"}
...     new_dict = {
...         key_to_keep: context[key_to_keep]
...         for key_to_keep in keys_to_keep
...         if key_to_keep in context
...     }
...     context.clear()
...     context.update(new_dict)

"""

pre_task_succeeded = django.dispatch.Signal()
""" Signal to add ``structlog`` bindings from ``celery``'s successful task.

:param logger: the logger to bind more metadata or override existing bound metadata
:param result: result of the succeeding task

>>> from django.dispatch import receiver
>>> from django_structlog.celery import signals
>>> import structlog
>>>
>>> @receiver(signals.pre_task_succeeded)
... def receiver_pre_task_succeeded(sender, signal, logger=None, result=None, **kwargs):
...     structlog.contextvars.bind_contextvars(result=str(result))

"""
