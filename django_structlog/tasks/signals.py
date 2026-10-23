import django.dispatch

bind_extra_task_metadata = django.dispatch.Signal()
""" Signal to add extra ``structlog`` bindings from ``django.tasks``'s task.

:param task_result: the ``TaskResult`` of the task being run
:param logger: the logger to bind more metadata or override existing bound metadata

>>> from django.dispatch import receiver
>>> from django_structlog.tasks import signals
>>> import structlog
>>>
>>> @receiver(signals.bind_extra_task_metadata)
... def receiver_bind_extra_task_metadata(sender, signal, task_result=None, logger=None, **kwargs):
...     structlog.contextvars.bind_contextvars(task_backend=task_result.backend)

"""


modify_context_before_task_publish = django.dispatch.Signal()
""" Signal to modify context passed over to ``django.tasks`` task's context. You must modify the ``context`` dict.

The ``context`` is stored in the ``django_structlog`` cache and must therefore be serializable by that cache backend.

:param context: the context dict that will be passed over to the task runner's logger

>>> from django.dispatch import receiver
>>> from django_structlog.tasks import signals
>>>
>>> @receiver(signals.modify_context_before_task_publish)
... def receiver_modify_context_before_task_publish(sender, signal, context, **kwargs):
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
""" Signal to add ``structlog`` bindings from ``django.tasks``'s successful task.

:param logger: the logger to bind more metadata or override existing bound metadata
:param task_result: the ``TaskResult`` of the succeeding task

>>> from django.dispatch import receiver
>>> from django_structlog.tasks import signals
>>> import structlog
>>>
>>> @receiver(signals.pre_task_succeeded)
... def receiver_pre_task_succeeded(sender, signal, logger=None, task_result=None, **kwargs):
...     structlog.contextvars.bind_contextvars(result=str(task_result.return_value))

"""
