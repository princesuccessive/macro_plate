CELERY_BROKER = 'redis://redis/'
CELERY_BACKEND = 'redis://redis/'

CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'

CELERY_ACCEPT_CONTENT = ['pickle', 'json']
