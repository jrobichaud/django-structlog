from django.conf.urls import url

from django_structlog_demo_project.users.views import (
    user_list_view,
    user_redirect_view,
    user_update_view,
    user_detail_view,
)

app_name = "users"
urlpatterns = [
    url(r"^$", view=user_list_view, name="list"),
    url(r"~redirect/", view=user_redirect_view, name="redirect"),
    url(r"~update/", view=user_update_view, name="update"),
    url(r"^(?P<username>\w+)/", view=user_detail_view, name="detail"),
]
