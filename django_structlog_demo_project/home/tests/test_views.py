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
