import structlog

from . import signals


logger = structlog.getLogger(__name__)


def receiver_before_task_publish(sender=None, headers=None, body=None, **kwargs):
    immutable_logger = structlog.threadlocal.as_immutable(logger)
    # noinspection PyProtectedMember
    context = dict(immutable_logger._context)
    if 'task_id' in context:
        context['parent_task_id'] = context.pop('task_id')
    headers['__django_structlog__'] = context


def receiver_after_task_publish(sender=None, headers=None, body=None, **kwargs):
    logger.info('task_enqueued', child_task_id=headers['id'], child_task_name=headers['task'])


def receiver_task_pre_run(task_id, task, *args, **kwargs):
    logger.new()
    logger.bind(task_id=task_id)
    signals.bind_extra_task_metadata.send(sender=receiver_task_pre_run, task=task, logger=logger)
    metadata = getattr(task.request, '__django_structlog__', {})
    logger.bind(**metadata)


def receiver_task_retry(request=None, reason=None, einfo=None, **kwargs):
    logger.warning('task_retrying', reason=reason)


def receiver_task_success(result=None, **kwargs):
    logger.info('task_succeed', result=str(result))


def receiver_task_failure(task_id=None, exception=None, traceback=None, einfo=None, *args, **kwargs):
    logger.error('task_failed', error=str(exception))


def receiver_task_revoked(request=None, terminated=None, signum=None, expired=None, **kwargs):
    logger.warning('task_revoked', terminated=terminated, signum=signum, expired=expired)


def receiver_task_unknown(message=None, exc=None, name=None, id=None, **kwargs):
    logger.error('task_not_found', message=message)


def receiver_task_rejected(message=None, exc=None, **kwargs):
    logger.error('task_rejected', message=message)
