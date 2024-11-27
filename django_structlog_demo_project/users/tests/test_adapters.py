import pytest

from django_structlog_demo_project.users.adapters import AccountAdapter

pytestmark = pytest.mark.django_db


class TestUserCreationForm:
    def test_account_adapter(self):
        assert AccountAdapter().is_open_for_signup(None)
