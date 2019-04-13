from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='django-structlog',
    version='0.0.1',
    author='Jules Robichaud-Gagnon',
    author_email='j.robichaudg+pypi@gmail.com',
    description='Structure logging for Django',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/jrobichaud/django-structlog',
    packages=[
        'django_structlog',
    ],
    install_requires=[
        'django>=1.11'
        'structlog',
        'django-ipware',
    ],
    license="MIT",
)
