import logging

import structlog


logger = structlog.wrap_logger(logger=logging.getLogger(__name__))


def receiver_before_task_publish(sender=None, headers=None, body=None, **kwargs):
    immutable_logger = structlog.threadlocal.as_immutable(logger)
    # noinspection PyProtectedMember
    context = immutable_logger._context
    headers['__django_structlog__'] = dict(context)


def receiver_after_task_publish(sender=None, headers=None, body=None, **kwargs):
    logger.info('Task enqueued', task_id=headers['id'])


def receiver_task_pre_run(task_id, task, *args, **kwargs):
    logger.new()
    logger.bind(task_id=task_id)
    metadata = getattr(task.request, '__django_structlog__', {})
    logger.bind(**metadata)


def receiver_task_retry(request=None, reason=None, einfo=None, **kwargs):
    logger.warning('Task retry', reason=reason)


def receiver_task_success(result=None, **kwargs):
    logger.info('Task success', result=str(result))


def receiver_task_failure(task_id=None, exception=None, traceback=None, einfo=None, *args, **kwargs):
    logger.error('Task failure', error=str(exception))


def receiver_task_revoked(request=None, terminated=None, signum=None, expired=None, **kwargs):
    logger.warning('Task revoked', terminated=terminated, signum=signum, expired=expired)


def receiver_task_unknown(message=None, exc=None, name=None, id=None, **kwargs):
    logger.error('Task unknown', message=message)


def receiver_task_rejected(message=None, exc=None, **kwargs):
    logger.error('Task rejected', message=message)


class CeleryMiddleware(object):

    def __init__(self, get_response=None):
        self.get_response = get_response
        connect_signals()

    def __call__(self, request):
        return self.get_response(request)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        disconnect_signals()


def connect_signals():
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
    before_task_publish.connect(receiver_before_task_publish)
    after_task_publish.connect(receiver_after_task_publish)
    task_prerun.connect(receiver_task_pre_run)
    task_retry.connect(receiver_task_retry)
    task_success.connect(receiver_task_success)
    task_failure.connect(receiver_task_failure)
    task_revoked.connect(receiver_task_revoked)
    task_unknown.connect(receiver_task_unknown)
    task_rejected.connect(receiver_task_rejected)


def disconnect_signals():
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
    before_task_publish.disconnect(receiver_before_task_publish)
    after_task_publish.disconnect(receiver_after_task_publish)
    task_prerun.disconnect(receiver_task_pre_run)
    task_retry.disconnect(receiver_task_retry)
    task_success.disconnect(receiver_task_success)
    task_failure.disconnect(receiver_task_failure)
    task_revoked.disconnect(receiver_task_revoked)
    task_unknown.disconnect(receiver_task_unknown)
    task_rejected.disconnect(receiver_task_rejected)
