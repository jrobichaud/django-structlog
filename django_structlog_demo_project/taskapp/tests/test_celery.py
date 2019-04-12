import pytest

from .. import celery

pytestmark = pytest.mark.django_db


class TestSuccessfulTask:
    def test(self, caplog):
        celery.successful_task(foo='bar')
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.msg['event'] == "This is a successful task"


class TestFailingTask:
    def test(self):
        with pytest.raises(Exception) as e:
            celery.failing_task(foo='bar')
        assert str(e.value) == 'This is a failed task'
