from invoke import task

from . import common, django, is_local_python, start
from .common import print_green

##############################################################################
# Common stuff
##############################################################################

__all__ = ('notebooks',)


@task
def notebooks(context, params=None):
    """Run jupyter notebooks (if available) from docs/jupyter folder

    If you get error related to sqlite - try to install sqlite, sqlite_devel
    linux packages first, then recompile python3 with sqlite support
    With pyenv it's easier - as you can install deps and then simply erase
    version of python and then install it again - it will compile with sqlite
    support automatically

    All jupyter notebooks are by default stored in docs/jupyter folder
    which you can change in your local.py

    Jupyter sees all Django apps models due to docs/jupyter/ipython_config.py
    file - see how paths are added inside.

    See more info on this problem here
    https://stackoverflow.com/questions/1210664/no-module-named-sqlite3

    Additional params are described here:
        http://django-extensions.readthedocs.io/en/latest/shell_plus.html
    """

    print_green("Run jupyter notebooks")
    if is_local_python:
        django.manage(context, 'shell_plus --notebook {}'.format(params or ""))
    else:
        start.docker_compose_run(
            context,
            '--service-ports web python3 manage.py shell_plus --notebook'
        )
