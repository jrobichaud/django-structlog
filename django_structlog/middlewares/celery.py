import logging

import structlog

logger = structlog.wrap_logger(logger=logging.getLogger(__name__))


class CeleryMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        self.receiver_before_task_publish = None
        self.receiver_after_task_publish = None
        self.initialize_celery()

    def __call__(self, request):
        return self.get_response(request)

    def initialize_celery(self):
        from celery.signals import (
            before_task_publish,
            after_task_publish,
        )

        @before_task_publish.connect
        def receiver_before_task_publish(sender=None, headers=None, body=None, **kwargs):
            # info = headers if 'task' in headers else body
            pass

        self.receiver_before_task_publish = receiver_before_task_publish

        @after_task_publish.connect
        def receiver_after_task_publish(sender=None, headers=None, body=None, **kwargs):
            info = headers if 'task' in headers else body
            logger.info('Task enqueued', task_id=info['id'])

        self.receiver_after_task_publish = receiver_after_task_publish
