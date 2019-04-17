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