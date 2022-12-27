web: python3 manage.py collectstatic --noinput && uwsgi --static-map /static=/workspace/static --ini uwsgi.ini

celery_worker: celery -A config.celery:app worker -l info
celery_beat: celery -A config.celery:app beat -l info -S django

migrations: python3 manage.py migrate

tests: pytest
shell_plus: python3 manage.py shell_plus --ipython
dbshell: python3 manage.py dbshell
debug: python3 manage.py collectstatic --noinput && python3 manage.py runserver 0.0.0.0:$PORT

freeze: sleep 3000
