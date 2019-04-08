from setuptools import find_packages, setup


setup(
    name='django-structlog',
    version='0.0.1',
    author='Jules Robichaud-Gagnon',
    author_email='j.robichaudg+pypi@gmail.com',
    description='For using structlog in Django',
    url='https://github.com/plumdog/django_migration_testcase',
    packages=[
        'django_structlog',
    ],
    install_requires=[
        'structlog'
    ],
    license="MIT",
)
