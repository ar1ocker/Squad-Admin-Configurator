#!/bin/sh
echo Wait 5 seconds for database initialization
sleep 5

echo Start migrations
python3 manage.py migrate --noinput

echo Run application
gunicorn "squad_admin_configurator.wsgi:application" --bind 0:8000 &
echo Run cronloop
python3 manage.py cronloop -s 300 &

# Wait for any process to exit
wait -n
exit $?