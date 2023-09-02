FROM python:3.10-slim

WORKDIR /squad-admin-configurator

COPY ./ ./

RUN pip3 install -r ./requirements.txt --no-cache-dir

RUN python3 ./manage.py collectstatic --no-input

RUN chmod -R o+x static

CMD ["gunicorn", "squad_admin_configurator.wsgi:application", "--bind", "0:8000"]
