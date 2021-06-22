from setuptools import setup, find_namespace_packages

import django_structlog

with open("README.rst", "r") as fh:
    long_description = fh.read()


setup(
    name="django-structlog",
    version=django_structlog.__version__,
    author="Jules Robichaud-Gagnon",
    author_email="j.robichaudg+pypi@gmail.com",
    description="Structured Logging for Django",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/jrobichaud/django-structlog",
    packages=find_namespace_packages(
        include=["django_structlog", "django_structlog.*"]
    ),
    install_requires=["django>=1.11", "structlog", "django-ipware"],
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Framework :: Django",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: System :: Logging",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
