from invoke import task

from . import common, is_local_python
from .common import print_green

##############################################################################
# Mkdocs
##############################################################################

__all__ = ('sphinx',)


##############################################################################
# Sphinx
##############################################################################

@task
def sphinx(context):
    """Run watchdog to autobuild sphinx documentation

    This command starts docker container with sphinx and you can see sphinx
    docs at http://127.0.0.1:8001

    Also when you edit docs, browser will automatically reload page after
    rebuild
    """
    print_green("Starting sphinx")

    if is_local_python:
        context.run('sphinx-autobuild docs .dev/sphinx-docs -H 0.0.0.0 -p 8001 '
              '-i ".git/*" ')
    else:
        context.run('docker-compose up sphinx')
