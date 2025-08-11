FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN adduser -u 5678 --disabled-password --gecos "" appuser

COPY ./requirements.txt ./

RUN pip3 install -r requirements.txt --no-cache-dir

COPY ./ ./

RUN chown -R appuser /app

RUN chown -R appuser /usr/local/lib/python3.10/site-packages/django_cron/
RUN chmod o+x migrations.sh

USER appuser

RUN python3 manage.py collectstatic --noinput --clear
