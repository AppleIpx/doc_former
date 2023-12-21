#! /bin/bash

python3 manage.py makemigrations users

python3 manage.py makemigrations assignment

python3 manage.py makemigrations api

python3 manage.py migrate --no-input

python3 manage.py collectstatic --no-input

#celery -A doc_former worker -l info

#python3 manage.py filling_db

gunicorn doc_former.wsgi:application --bind 0.0.0.0:8000