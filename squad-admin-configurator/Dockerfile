FROM python:3.10-alpine3.18

WORKDIR /squad-admin-configurator

RUN apk add --no-cache tini

COPY ./ ./

RUN pip3 install -r ./requirements.txt --no-cache-dir
RUN mkdir static
RUN chmod -R o+x static

RUN chmod +x start.sh

ENTRYPOINT ["/sbin/tini", "--"]

CMD ["/bin/sh", "./start.sh"]
