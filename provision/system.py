from invoke import task

from . import common
from .common import print_green

##############################################################################
# System shortcuts
##############################################################################

__all__ = ('gitmessage', 'chown', 'hooks',)


def chown(context):
    """Shortcut for owning apps dir by current user after some files were
    generated using docker-compose (migrations, new app, etc)
    """
    context.run('sudo chown ${USER}:${USER} -R apps')


def gitmessage(context):
    """Set default .gitmessage
    """
    print_green("Deploy git commit message template")
    context.run('echo "[commit]" >> .git/config')
    context.run('echo "  template = .gitmessage" >> .git/config')


@task
def hooks(context):
    """Install git hooks

    Used during ``build``
    """
    print_green("GitHooks copy to .git")
    context.run('mkdir -p .git/hooks')
    context.run('cp .git-hooks/* .git/hooks/')
