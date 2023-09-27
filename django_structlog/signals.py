import django.dispatch


bind_extra_request_metadata = django.dispatch.Signal()
""" Signal to add extra ``structlog`` bindings from ``django``'s request.

:param logger: the logger to bind more metadata or override existing bound metadata

>>> from django.contrib.sites.shortcuts import get_current_site
>>> from django.dispatch import receiver
>>> from django_structlog import signals
>>> import structlog
>>>
>>> @receiver(signals.bind_extra_request_metadata)
... def bind_domain(request, logger, **kwargs):
...     current_site = get_current_site(request)
...     structlog.contextvars.bind_contextvars(domain=current_site.domain)

"""

bind_extra_request_finished_metadata = django.dispatch.Signal()
""" Signal to add extra ``structlog`` bindings from ``django``'s finished request and response.

:param logger: the logger to bind more metadata or override existing bound metadata
:param response: the response resulting of the request

>>> from django.contrib.sites.shortcuts import get_current_site
>>> from django.dispatch import receiver
>>> from django_structlog import signals
>>> import structlog
>>>
>>> @receiver(signals.bind_extra_request_finished_metadata)
... def bind_domain(request, logger, response, **kwargs):
...     current_site = get_current_site(request)
...     structlog.contextvars.bind_contextvars(domain=current_site.domain)

"""

bind_extra_request_failed_metadata = django.dispatch.Signal()
""" Signal to add extra ``structlog`` bindings from ``django``'s failed request and exception.

:param logger: the logger to bind more metadata or override existing bound metadata
:param exception: the exception resulting of the request

>>> from django.contrib.sites.shortcuts import get_current_site
>>> from django.dispatch import receiver
>>> from django_structlog import signals
>>> import structlog
>>>
>>> @receiver(signals.bind_extra_request_failed_metadata)
... def bind_domain(request, logger, exception, **kwargs):
...     current_site = get_current_site(request)
...     structlog.contextvars.bind_contextvars(domain=current_site.domain)

"""

update_failure_response = django.dispatch.Signal()
""" Signal to update response failure response before it is returned.

:param request: the request returned by the view
:param response: the response resulting of the request
:param logger: the logger
:param exception: the exception

>>> from django.dispatch import receiver
>>> from django_structlog import signals
>>> import structlog
>>>
>>> @receiver(signals.update_failure_response)
... def add_request_id_to_error_response(request, response, logger, exception, **kwargs):
...     context = structlog.contextvars.get_merged_contextvars(logger)
...     response['X-Request-ID'] = context["request_id"]

"""
