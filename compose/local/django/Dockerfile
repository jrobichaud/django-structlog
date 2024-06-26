#syntax=docker/dockerfile:1.4
ARG PYTHON_VERSION

FROM python:${PYTHON_VERSION}-alpine as python

FROM python AS python-build-stage

ARG REQUIREMENTS_FILE=local.txt


RUN <<EOF
  apk update
  # CFFI dependencies
  apk add libffi-dev py-cffi
  # https://docs.djangoproject.com/en/dev/ref/django-admin/#dbshell
  apk add postgresql-client
EOF

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements

RUN pip wheel --wheel-dir /usr/src/app/wheels \
  -r /requirements/${REQUIREMENTS_FILE}

FROM python as python-run-stage

ENV PYTHONUNBUFFERED 1

RUN <<EOF
  apk update
  # Translations dependencies
  apk add gettext
  # https://docs.djangoproject.com/en/dev/ref/django-admin/#dbshell
  apk add postgresql-client
EOF

COPY --from=python-build-stage /usr/src/app/wheels  /wheels/

RUN <<EOF
  pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/*
  rm -rf /wheels/
EOF

COPY ./compose/local/django/entrypoint /entrypoint
RUN sed -i 's/\r//' /entrypoint
RUN chmod +x /entrypoint

COPY ./compose/local/django/start /start
RUN sed -i 's/\r//' /start
RUN chmod +x /start

COPY ./compose/local/django/start_asgi /start_asgi
RUN sed -i 's/\r//' /start_asgi
RUN chmod +x /start_asgi

COPY ./compose/local/django/start_wsgi /start_wsgi
RUN sed -i 's/\r//' /start_wsgi
RUN chmod +x /start_wsgi

COPY ./compose/local/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r//' /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./compose/local/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r//' /start-celerybeat
RUN chmod +x /start-celerybeat

COPY ./compose/local/django/celery/flower/start /start-flower
RUN sed -i 's/\r//' /start-flower
RUN chmod +x /start-flower

WORKDIR /app

RUN addgroup --system django \
    && adduser --system --ingroup django django

RUN chown django:django /app

ENTRYPOINT ["/entrypoint"]
