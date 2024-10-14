import logging

import structlog
from django.test import TestCase
from django.core.management import BaseCommand, call_command
from django_extensions.management.utils import signalcommand


class TestCommands(TestCase):
    def test_command(self):
        class Command(BaseCommand):
            @signalcommand
            def handle(self, *args, **options):
                structlog.getLogger("command").info("command_event")

        with (
            self.assertLogs("command", logging.INFO) as command_log_results,
            self.assertLogs(
                "django_structlog.commands", logging.INFO
            ) as django_structlog_commands_log_results,
        ):
            call_command(Command())

        self.assertEqual(1, len(command_log_results.records))
        record = command_log_results.records[0]
        self.assertEqual("command_event", record.msg["event"])
        self.assertIn("command_id", record.msg)

        self.assertEqual(2, len(django_structlog_commands_log_results.records))
        record = django_structlog_commands_log_results.records[0]
        self.assertEqual("command_started", record.msg["event"])
        self.assertIn("command_id", record.msg)
        record = django_structlog_commands_log_results.records[1]
        self.assertEqual("command_finished", record.msg["event"])
        self.assertIn("command_id", record.msg)

    def test_nested_command(self):
        class Command(BaseCommand):
            @signalcommand
            def handle(self, *args, **options):
                logger = structlog.getLogger("command")
                logger.info("command_event_1")
                call_command(NestedCommand())
                logger.info("command_event_2")

        class NestedCommand(BaseCommand):
            @signalcommand
            def handle(self, *args, **options):
                structlog.getLogger("nested_command").info("nested_command_event")

        with (
            self.assertLogs("command", logging.INFO) as command_log_results,
            self.assertLogs("nested_command", logging.INFO),
            self.assertLogs(
                "django_structlog.commands", logging.INFO
            ) as django_structlog_commands_log_results,
        ):
            call_command(Command())

        self.assertEqual(2, len(command_log_results.records))
        command_event_1 = command_log_results.records[0]
        self.assertEqual("command_event_1", command_event_1.msg["event"])
        self.assertIn("command_id", command_event_1.msg)
        command_event_2 = command_log_results.records[1]
        self.assertEqual("command_event_2", command_event_2.msg["event"])
        self.assertIn("command_id", command_event_2.msg)
        self.assertEqual(
            command_event_1.msg["command_id"], command_event_2.msg["command_id"]
        )

        self.assertEqual(4, len(django_structlog_commands_log_results.records))
        command_started_1 = django_structlog_commands_log_results.records[0]
        self.assertEqual("command_started", command_started_1.msg["event"])
        self.assertIn("command_id", command_started_1.msg)

        command_started_2 = django_structlog_commands_log_results.records[1]
        self.assertEqual("command_started", command_started_2.msg["event"])
        self.assertIn("command_id", command_started_2.msg)
        self.assertIn("parent_command_id", command_started_2.msg)
        self.assertEqual(
            command_started_1.msg["command_id"],
            command_started_2.msg["parent_command_id"],
        )

        command_finished_1 = django_structlog_commands_log_results.records[2]
        self.assertEqual("command_finished", command_finished_1.msg["event"])
        self.assertIn("command_id", command_finished_1.msg)
        self.assertIn("parent_command_id", command_finished_1.msg)
        self.assertEqual(
            command_started_1.msg["command_id"],
            command_finished_1.msg["parent_command_id"],
        )

        command_finished_2 = django_structlog_commands_log_results.records[3]
        self.assertEqual("command_finished", command_finished_2.msg["event"])
        self.assertIn("command_id", command_finished_2.msg)
        self.assertNotIn("parent_command_id", command_finished_2.msg)
        self.assertEqual(
            command_event_1.msg["command_id"], command_finished_2.msg["command_id"]
        )
