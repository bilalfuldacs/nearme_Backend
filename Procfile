release: python manage.py migrate && python manage.py populate_categories
web: gunicorn backend_api.wsgi:application --bind 0.0.0.0:$PORT --log-file -

