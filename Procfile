web: gunicorn club_platform.wsgi:application
web: gunicorn club_platform.wsgi --log-file - 
web: python manage.py migrate && gunicorn club_platform.wsgi
