import logging

import pytest

from .. import tasks

pytestmark = pytest.mark.django_db


class TestDjangoTask:
    def test(self, caplog):
        with caplog.at_level(
            logging.INFO, logger="django_structlog_demo_project.tasks"
        ):
            task_result = tasks.django_task.enqueue()
        assert task_result.return_value == "ok"

        assert len(caplog.records) == 3
        record = caplog.records[1]
        assert (
            record.msg["event"]
            == "This is a Django 6 native task using the built-in task framework"
        )

    def test_failing(self, caplog):
        with caplog.at_level(
            logging.INFO, logger="django_structlog_demo_project.tasks"
        ):
            tasks.django_failing_task.enqueue()

        assert len(caplog.records) == 3
        record = caplog.records[1]
        assert record.msg["event"] == "This is a failing Django 6 native task"
