import os

from invoke import task

from . import (
    common,
    data,
    django,
    docker,
    is_local_python,
    rabbitmq,
    system,
    tests,
)
from .common import print_green

##############################################################################
# Build project locally
##############################################################################

__all__ = (
    'build',
    'init',
    'install_tools',
    'compile_requirements',
    'recompile_rebuild',
)


def copylocal(context, force_update=True):
    """Copy local settings from template

    Args:
        force_update(bool): rewrite file if exists or not
    """
    local_settings = 'config/settings/local.py'
    local_template = 'config/settings/local.py.template'

    if force_update or not os.path.isfile(local_settings):
        context.run(
            ' '.join(['cp', local_template, local_settings])
        )


@task
def build(context, container=None):
    """Build python environ"""
    if is_local_python:
        install_requirements(context)
    else:
        print_green("Rebuilding docker {} container".format(container))

        cmd = 'docker-compose build'
        if container:
            cmd = '{} {}'.format(cmd, container)
        context.run(cmd)


@task
def init(context, clean=False):
    """Buld project from scratch
    """

    print_green("Initial assembly of all dependencies")
    system.hooks(context)
    system.gitmessage(context)
    install_tools(context)
    compile_requirements(context)
    if clean:
        docker.clear()
    copylocal(context)
    build(context)
    django.makemigrations(context)
    django.migrate(context)
    django.createsuperuser(context)
    rabbitmq.init(context)
    tests.run(context)

    # if this is first start of the project
    # then the following line will generate exception
    # informing first developer to make factories
    try:
        success = data.sync_from_remote(context)
        if not success:
            data.load_fixtures(context)
    except NotImplementedError:
        print(
            "Awesome, almost everything is Done! \n"
            "You're the first developer - pls generate factories \n"
            "for test data and setup development environment")

    print_green(
        "Type `MACROPLATE_ENVIRONMENT=local fab django.run` to start web app"
    )


##############################################################################
# Manage dependencies
##############################################################################

def install_tools(context):
    """Install shell/cli dependencies, and tools needed to install requirements

    Define your dependencies here, for example
    local('sudo npm -g install ngrok')
    """
    context.run('pip install --upgrade setuptools pip pip-tools')


def install_requirements(context, env='development'):
    """Install local development requirements"""
    print_green("Install requirements with pip from {env}.txt".format(env=env))
    context.run('pip install -r requirements/{env}.txt'.format(env=env))


@task
def compile_requirements(context, u=False):
    """Compile requirements with pip-compile"""
    print_green("Compile requirements with pip-compile")
    upgrade = '-U' if u else ''
    in_files = [
        'requirements/development.in',
        'requirements/production.in',
    ]
    for in_file in in_files:
        context.run(
            'pip-compile -q {in_file} {upgrade}'.format(
                in_file=in_file,
                upgrade=upgrade),
        )


@task
def recompile_rebuild(context, container='web'):
    """Recompile dependencies and re-build docker containers"""
    compile_requirements(context)
    build(context, container)
