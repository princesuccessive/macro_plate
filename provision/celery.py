from invoke import task

from . import is_local_python
from .docker import docker_compose_run


@task
def run(context):
    """Start celery worker."""
    if is_local_python:
        context.run(
            'celery --app config.celery:app '
            'worker --beat --scheduler=django --loglevel=info',
        )
    else:
        docker_compose_run(context, 'celery_worker')
