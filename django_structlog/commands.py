import structlog
import uuid

logger = structlog.getLogger(__name__)
stack = []


def pre_receiver(sender, *args, **kwargs):
    command_id = str(uuid.uuid4())
    if len(stack):
        parent_command_id, _ = stack[-1]
        tokens = structlog.contextvars.bind_contextvars(
            parent_command_id=parent_command_id, command_id=command_id
        )
    else:
        tokens = structlog.contextvars.bind_contextvars(command_id=command_id)
    stack.append((command_id, tokens))

    logger.info(
        "command_started",
        command_name=sender.__module__.replace(".management.commands", ""),
    )


def post_receiver(sender, outcome, *args, **kwargs):
    logger.info("command_finished")

    if len(stack):
        command_id, tokens = stack.pop()
        structlog.contextvars.reset_contextvars(**tokens)


def init_command_signals():
    try:
        from django_extensions.management.signals import pre_command, post_command
    except ModuleNotFoundError:  # pragma: no cover
        return

    pre_command.connect(pre_receiver)
    post_command.connect(post_receiver)
