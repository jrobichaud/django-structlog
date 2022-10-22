FROM python:3.10-alpine

ENV PYTHONUNBUFFERED 1

RUN apk update \
  && apk add --virtual build-dependencies \
     build-base

WORKDIR /app

# Requirements are installed here to ensure they will be cached.
COPY ./docs/requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./compose/local/docs/start /start
RUN sed -i 's/\r//' /start
RUN chmod +x /start
