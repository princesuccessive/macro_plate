from invoke import task

from . import common, django, is_local_python, start
from .common import print_green

##############################################################################
# Test commands
##############################################################################

__all__ = (
    'run',
    'run_clear',
    'run_fast',
    'coverage',
)


@task
def run(context, path='', p='--parallel --failfast'):
    """Run django tests with ``extra`` args for ``p`` tests.

    `p` means `params` - extra args for tests

    manage.py test <extra>
    """
    print_green("Tests {} running ".format(path))
    django.manage(context, ' '.join(['test', path, p]))


@task
def run_clear(context, path=''):
    """Alias for tests without `keepdb` flag"""
    run(context, path=path, p='--noinput --parallel --failfast')


@task
def run_fast(context, path=''):
    """Run django tests as fast as possible.

    No migrations, keep DB, parallel.

    manage.py test --keepdb --failfast --parallel <path>
    """
    run(context, path=path, p='--keepdb --failfast --parallel')


@task
def coverage(context, extra='--keepdb --failfast'):
    """Generate and display test-coverage"""
    print_green("Calculate and display code coverage")
    execute = context.run if is_local_python else start.run_web

    execute(' '.join(['coverage run manage.py test', extra]))
    execute('coverage html')
    context.run('xdg-open htmlcov/index.html & sleep 3')
