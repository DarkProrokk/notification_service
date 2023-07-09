FROM python:3.11-alpine

COPY requirements.txt /temp/requirements.txt
COPY notification_services /notification_services/
WORKDIR /notification_services
EXPOSE 8000

RUN apk add postgresql-client build-base postgresql-dev

RUN pip install -r /temp/requirements.txt

RUN adduser --disabled-password notification_services-user

user notification_services-user