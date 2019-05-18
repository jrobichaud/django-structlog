import pytest

from django_structlog_demo_project.users.adapters import (
    SocialAccountAdapter,
    AccountAdapter,
)

pytestmark = pytest.mark.django_db


class TestUserCreationForm:
    def test_account_adapter(self):
        assert AccountAdapter().is_open_for_signup(None)

    def test_social_account_adapter(self):
        assert SocialAccountAdapter().is_open_for_signup(None, None)
