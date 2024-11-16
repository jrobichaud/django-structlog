from __future__ import annotations

from typing import List, Tuple, Mapping, Any, Type, TYPE_CHECKING

import structlog
import uuid

from django_extensions.management.signals import pre_command, post_command

if TYPE_CHECKING:
    import contextvars

logger = structlog.getLogger(__name__)


class DjangoCommandReceiver:
    def __init__(self) -> None:
        self.stack: List[Tuple[str, Mapping[str, contextvars.Token[Any]]]] = []

    def pre_receiver(self, sender: Type[Any], *args: Any, **kwargs: Any) -> None:
        command_id = str(uuid.uuid4())
        if len(self.stack):
            parent_command_id, _ = self.stack[-1]
            tokens = structlog.contextvars.bind_contextvars(
                parent_command_id=parent_command_id, command_id=command_id
            )
        else:
            tokens = structlog.contextvars.bind_contextvars(command_id=command_id)
        self.stack.append((command_id, tokens))

        logger.info(
            "command_started",
            command_name=sender.__module__.replace(".management.commands", ""),
        )

    def post_receiver(
        self, sender: Type[Any], outcome: str, *args: Any, **kwargs: Any
    ) -> None:
        logger.info("command_finished")

        if len(self.stack):  # pragma: no branch
            command_id, tokens = self.stack.pop()
            structlog.contextvars.reset_contextvars(**tokens)

    def connect_signals(self) -> None:
        pre_command.connect(self.pre_receiver)
        post_command.connect(self.post_receiver)
