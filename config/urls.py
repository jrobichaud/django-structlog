from django.conf import settings
from django.conf.urls import include
from django.urls import re_path
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views

from django_structlog_demo_project.home import views, api_views


def uncaught_exception_view(request):
    raise Exception("Uncaught Exception")


urlpatterns = [
    re_path(r"^$", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    re_path(
        r"^success_task$", views.enqueue_successful_task, name="enqueue_successful_task"
    ),
    re_path(r"^failing_task$", views.enqueue_failing_task, name="enqueue_failing_task"),
    re_path(r"^nesting_task$", views.enqueue_nesting_task, name="enqueue_nesting_task"),
    re_path(r"^unknown_task$", views.enqueue_unknown_task, name="enqueue_unknown_task"),
    re_path(
        r"^rejected_task$", views.enqueue_rejected_task, name="enqueue_rejected_task"
    ),
    re_path(r"^raise_exception", views.raise_exception, name="raise_exception"),
    re_path(
        r"^standard_logger", views.log_with_standard_logger, name="standard_logger"
    ),
    re_path(r"^async_view", views.async_view, name="async_view"),
    re_path(r"^api_view$", api_views.home_api_view, name="api_view"),
    re_path(
        r"^about/", TemplateView.as_view(template_name="pages/about.html"), name="about"
    ),
    re_path(r"^revoke_task", views.revoke_task, name="revoke_task"),
    # Django Admin, use {% url 'admin:index' %}
    re_path(settings.ADMIN_URL, admin.site.urls),
    # User management
    re_path(
        r"^users/",
        include("django_structlog_demo_project.users.urls", namespace="users"),
    ),
    re_path(r"^accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        re_path(
            r"^400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        re_path(
            r"^403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        re_path(
            r"^404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        re_path(r"^500/", default_views.server_error),
        re_path(r"^uncaught_exception/", uncaught_exception_view),
    ]
