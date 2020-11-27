import pytest

from .. import views

pytestmark = pytest.mark.django_db


class TestEnqueueSuccessfulTask:
    def test(self):
        response = views.enqueue_successful_task(None)
        assert response.status_code == 201


class TestEnqueueFailingTask:
    def test(self):
        response = views.enqueue_failing_task(None)
        assert response.status_code == 201


class TestEnqueueNestingTask:
    def test(self):
        response = views.enqueue_nesting_task(None)
        assert response.status_code == 201


class TestRaiseException:
    def test(self):
        with pytest.raises(Exception) as e:
            views.raise_exception(None)
        assert str(e.value) == "This is a view raising an exception."


class TestLogWithStandardLogger:
    def test(self):
        response = views.log_with_standard_logger(None)
        assert response.status_code == 200
