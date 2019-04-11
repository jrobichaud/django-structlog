import logging
import json

import structlog

from django.conf import settings

logger = structlog.wrap_logger(logger=logging.getLogger(__name__))


class CeleryMiddleware(object):
    context_to_pass = [
        'request_id',
        'user_id',
    ]

    def __init__(self, get_response):
        self.get_response = get_response
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

        @before_task_publish.connect
        def receiver_before_task_publish(sender=None, headers=None, body=None, **kwargs):
            if settings.CELERY_TASK_SERIALIZER == 'json':
                decoded_kwargs = json.loads(headers['kwargsrepr'])
                data_to_pass = {}
                immutable_logger = structlog.threadlocal.as_immutable(logger)
                context = immutable_logger._context
                for key in self.context_to_pass:
                    if key in context:
                        data_to_pass[key] = context[key]
                decoded_kwargs['__django_structlog__'] = data_to_pass

                headers['kwargsrepr'] = json.dumps(decoded_kwargs)

        @after_task_publish.connect
        def receiver_after_task_publish(sender=None, headers=None, body=None, **kwargs):
            logger.info('Task enqueued', task_id=headers['id'])

        @task_prerun.connect
        def receiver_task_pre_run(task_id, task, request, *args, **kwargs):
            logger.new()
            logger.bind(task_id=task_id)
            logger.bind(**kwargs.pop('__django_structlog__', {}))
            logger.info('Task started')

        @task_retry.connect
        def receiver_task_retry(request=None, reason=None, einfo=None, **kwargs):
            logger.warning('Task retry', reason=reason)

        @task_success.connect
        def receiver_task_success(result=None, **kwargs):
            logger.info('Task success', result=str(result))

        @task_failure.connect
        def receiver_task_failure(task_id=None, exception=None, traceback=None, einfo=None, *args, **kwargs):
            logger.error('Task failure', error=str(exception))

        @task_revoked.connect
        def receiver_task_revoked(request=None, terminated=None, signum=None, expired=None, **kwargs):
            logger.warning('Task revoked', terminated=terminated, signum=signum, expired=expired)

        @task_unknown.connect
        def receiver_task_unknown(message=None, exc=None, name=None, id=None, **kwargs):
            logger.error('Task unknown', message=message)

        @task_rejected.connect
        def receiver_task_rejected(message=None, exc=None, **kwargs):
            logger.error('Task rejected', message=message)

        self.receiver_before_task_publish = receiver_before_task_publish
        self.receiver_after_task_publish = receiver_after_task_publish
        self.receiver_task_pre_run = receiver_task_pre_run
        self.receiver_task_retry = receiver_task_retry
        self.receiver_task_success = receiver_task_success
        self.receiver_task_failure = receiver_task_failure
        self.receiver_task_revoked = receiver_task_revoked
        self.receiver_task_unknown = receiver_task_unknown
        self.receiver_task_rejected = receiver_task_rejected

    def __call__(self, request):
        return self.get_response(request)
