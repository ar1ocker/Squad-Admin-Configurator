FROM python:3.10-alpine3.18

ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN adduser -u 5678 --disabled-password --gecos "" appuser

RUN apk add --no-cache tini

COPY ./requirements.txt ./

RUN pip3 install -r requirements.txt --no-cache-dir

COPY ./ ./

RUN mkdir static
RUN chmod -R o+x static

RUN python3 manage.py collectstatic --noinput
RUN python3 manage.py makemigrations --noinput

RUN chmod +x start.sh

RUN chown -R appuser /app
USER appuser

ENTRYPOINT ["/sbin/tini", "--"]

CMD ["/bin/sh", "./start.sh"]
