import pytest
from django.core import management

from django_structlog_demo_project.command_examples.management.commands import (
    example_command,
)

pytestmark = pytest.mark.django_db


class TestCommand:
    def test_command(self):
        assert (
            management.call_command(example_command.Command(), "bar", verbosity=0)
            is None
        )
