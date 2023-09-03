#!/bin/sh
gunicorn "squad_admin_configurator.wsgi:application" --bind 0:8000 &
sleep 10; python3 manage.py cronloop -s 60 > /dev/null &

# Wait for any process to exit
wait -n
exit $?