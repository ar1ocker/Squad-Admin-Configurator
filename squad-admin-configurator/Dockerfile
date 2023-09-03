FROM python:3.10-alpine3.18

WORKDIR /squad-admin-configurator

COPY ./ ./

RUN pip3 install -r ./requirements.txt --no-cache-dir

RUN python3 ./manage.py collectstatic --no-input

RUN chmod -R o+x static

RUN chmod +x start.sh

CMD ./start.sh
