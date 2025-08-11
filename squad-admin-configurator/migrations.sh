#!/bin/sh
set -e

# У этих приложений из коробки не до конца созданные миграции
python3 manage.py makemigrations django_cron --noinput

python3 manage.py migrate --noinput
