import os

from invoke import task

from . import common, docker, start, system
from .common import print_green, print_red

##############################################################################
# Django commands and stuff
##############################################################################

__all__ = (
    'manage',
    'makemigrations',
    'migrate',
    'resetdb',
    'run',
    'shell',
    'dbshell',
)


@task
def manage(context, command):
    """Run ``manage.py`` command

    docker-compose run --rm web python3 manage.py <command>
    """
    docker.docker_compose_up(context, '-d postgres rabbitmq redis')
    return start.run_python(context, ' '.join(['manage.py', command]))


@task
def makemigrations(context):
    """Run makemigrations command and chown created migrations
    """
    print_green("Django: Make migrations")
    manage(context, 'makemigrations')
    system.chown(context)


@task
def migrate(context):
    """Run ``migrate`` command"""
    print_green("Django: Apply migrations")
    manage(context, 'migrate')


@task
def resetdb(context, apply_migrations=True):
    """Reset database to initial state (including test DB)"""
    print_green("Reset database to its initial state")
    manage(context, 'drop_test_database --noinput')
    manage(context, 'reset_db -c --noinput')
    if not apply_migrations:
        return
    makemigrations(context)
    migrate(context)
    createsuperuser(context)


def createsuperuser(context):
    """Create superuser
    """
    print_green("Create superuser")
    manage(context, 'createsuperuser')


@task
def run(context):
    """Run development web-server"""

    # start dependencies (so even in local mode this command
    # is working successfully
    # if you need more default services to be started define them
    # below, like celery, etc.
    docker.docker_compose_start(context, 'postgres redis rabbitmq')
    try:
        env = os.environ["MACROPLATE_ENVIRONMENT"]  # noqa
    except KeyError:
        print_red(
            "Please set the environment variable "
            "MACROPLATE_ENVIRONMENT, like=local")
        exit(1)
    print_green("Running web app")
    start.run_python(
        context,
        "manage.py runserver_plus 0.0.0.0:8000  --reloader-type stat --pm"
    )


@task
def shell(context, params=None):
    """Shortcut for manage.py shell_plus command

    Additional params available here:
        http://django-extensions.readthedocs.io/en/latest/shell_plus.html
    """
    print_green("Entering Django Shell")
    manage(context, 'shell_plus --ipython {}'.format(params or ""))


@task
def dbshell(context):
    """Open postgresql shell with credentials from either local or dev env"""
    print_green("Entering DB shell")
    manage(context, 'dbshell')
