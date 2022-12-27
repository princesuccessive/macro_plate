from functools import partial

from invoke import task

from . import is_local_python, start
from .common import print_green

##############################################################################
# Linters
##############################################################################

__all__ = ('all', 'pylama')

DEFAULT_FOLDERS = 'apps libs'


@task
def isort(context, path=DEFAULT_FOLDERS, params=''):
    """Sort python imports by the specified path.

    Usage:
        inv linters.isort
        # usage on selected file
        inv linters.isort --path='apps/users/models.py'
    """
    context.run(f'isort {path} {params}')


@task
def isort_check(context, path=DEFAULT_FOLDERS):
    """Command to fix imports formatting."""
    return isort(context, path=path, params="--check-only")


@task
def all(context, path=None):
    """Run all linters (JS, SASS, PEP8).

    Args:
        path(str): Path to selected file
    Usage:
        # is simple mode without report
        inv linters.all
        # usage on selected file
        inv linters.all --path='apps/users/models.py'
    """
    linters = (pylama, isort_check)
    for linter in linters:
        linter(context, path=path) if path else linter(context)


@task
def pylama(context, path=None):
    """Check codestyle by `pylama` inv file raise the `Aborting` exception with
    error code for avoid the error message used the `warn_only` for pylama used
    `pylama.ini` configuration file
    Args:
        path(str): Path to selected file
    Usage:
        # is simple mode without report
        inv linters.pylama
        # usage on selected file
        inv linters.pylama --path='apps/users/models.py'
    """
    print_green("Linters: Pylama running")
    execute = context.run if is_local_python else partial(
        start.run_web, context=context)
    return execute(command=f"pylama {path if path else DEFAULT_FOLDERS}")
