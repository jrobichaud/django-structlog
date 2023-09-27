ARG PYTHON_VERSION

FROM python:${PYTHON_VERSION}-alpine as python

FROM python AS python-build-stage

RUN apk update \
  && apk add --virtual build-dependencies \
     build-base

COPY ./docs/requirements.txt /requirements.txt

RUN pip wheel --wheel-dir /usr/src/app/wheels \
  -r /requirements.txt

FROM python AS python-run-stage

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY --from=python-build-stage /usr/src/app/wheels  /wheels/

RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
	&& rm -rf /wheels/

RUN addgroup --system django \
    && adduser --system --ingroup django django

RUN chown django:django /app

USER django

COPY ./compose/local/docs/start /start
RUN sed -i 's/\r//' /start
RUN chmod +x /start
