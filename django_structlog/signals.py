import django.dispatch


bind_extra_request_metadata = django.dispatch.Signal(
    providing_args=["request", "logger"]
)
""" Signal to add extra ``structlog`` bindings from ``django``'s request.

>>> from django.dispatch import receiver
>>> from django_structlog import signals
>>>
>>> @receiver(signals.bind_extra_request_metadata)
... def bind_user_email(request, logger, **kwargs):
...     logger.bind(user_email=getattr(request.user, 'email', ''))

"""

bind_extra_request_finished_metadata = django.dispatch.Signal(
    providing_args=["request", "logger", "response"]
)
""" Signal to add extra ``structlog`` bindings from ``django``'s finished request and response.

>>> from django.dispatch import receiver
>>> from django_structlog import signals
>>>
>>> @receiver(signals.bind_extra_request_finished_metadata)
... def bind_user_email(request, logger, response, **kwargs):
...     logger.bind(user_email=getattr(request.user, 'email', ''))

"""

bind_extra_request_failed_metadata = django.dispatch.Signal(
    providing_args=["request", "logger", "exception"]
)
""" Signal to add extra ``structlog`` bindings from ``django``'s failed request and exception.

>>> from django.dispatch import receiver
>>> from django_structlog import signals
>>>
>>> @receiver(signals.bind_extra_request_failed_metadata)
... def bind_user_email(request, logger, exception, **kwargs):
...     logger.bind(user_email=getattr(request.user, 'email', ''))

"""
