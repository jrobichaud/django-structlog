import django.dispatch


bind_extra_request_metadata = django.dispatch.Signal(providing_args=["request", "logger"])
""" Signal to add extra ``structlog`` bindings from ``django``'s request.

>>> from django.dispatch import receiver
>>> from django_structlog import signals
>>> 
>>> @receiver(signals.bind_extra_request_metadata)
... def bind_user_email(request, logger, **kwargs):
...     logger.bind(user_email=getattr(request.user, 'email', ''))

"""
