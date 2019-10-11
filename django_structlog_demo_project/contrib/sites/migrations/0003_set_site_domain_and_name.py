"""
To understand why this file is here, please read:

http://cookiecutter-django.readthedocs.io/en/latest/faq.html#why-is-there-a-django-contrib-sites-directory-in-cookiecutter-django
"""
from django.conf import settings
from django.db import migrations


def update_site_forward(apps, schema_editor):
    """Set site domain and name."""
    site_model = apps.get_model("sites", "Site")
    site_model.objects.update_or_create(
        id=settings.SITE_ID,
        defaults={"domain": "example.com", "name": "django_structlog_demo_project"},
    )


class Migration(migrations.Migration):

    dependencies = [("sites", "0002_alter_domain_unique")]

    operations = [migrations.RunPython(update_site_forward, migrations.RunPython.noop)]
