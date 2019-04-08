from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='django-structlog',
    version='0.0.1',
    author='Jules Robichaud-Gagnon',
    author_email='j.robichaudg+pypi@gmail.com',
    description='For using structlog in Django',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/plumdog/django_migration_testcase',
    packages=[
        'django_structlog',
    ],
    install_requires=[
        'structlog'
    ],
    license="MIT",
)
