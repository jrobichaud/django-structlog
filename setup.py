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
    python_requires=">=3.7",
    install_requires=["django>=3.2", "structlog>=21.4.0", "django-ipware", "asgiref"],
    extras_require={
        "celery": ["celery>=5.1"],
    },
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Logging",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
