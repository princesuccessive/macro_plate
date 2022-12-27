from . import docker, is_local_python

##############################################################################
# Run commands
##############################################################################

__all__ = (
    'run_web',
    'run_web_python',
    'run_local_python',
)


def run_web(context, command):
    """Run command in``web`` container.

    docker-compose run --rm web <command>
    """
    return docker.docker_compose_run(
        context,
        ' '.join(['--service-ports', 'web', command])
    )


def run_web_python(context, command):
    """Run command using web python iterpreter"""
    return run_web(context, ' '.join([
        './wait-for-it.sh',
        'postgres:5432',
        '--',
        'python3',
        command,
    ]))


def run_local_python(context, command):
    """Run command using local python interpreter"""
    return context.run(' '.join(['python3', command]))


if is_local_python:
    run_python = run_local_python
else:
    run_python = run_web_python
