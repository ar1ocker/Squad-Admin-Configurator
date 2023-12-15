#!/bin/sh
echo Collect static files
python3 manage.py collectstatic --noinput

echo Wait 5 seconds for database initialization
sleep 5

echo Start migrations
python3 manage.py makemigrations --noinput
python3 manage.py migrate

echo Run application
gunicorn "squad_admin_configurator.wsgi:application" --bind 0:8000 &
echo Run cronloop
python3 manage.py cronloop -s 300 > /dev/null &

# Wait for any process to exit
wait -n
exit $?