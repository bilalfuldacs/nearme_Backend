release: python manage.py migrate && python manage.py populate_categories
web: gunicorn backend_api.wsgi --log-file - --workers 3

