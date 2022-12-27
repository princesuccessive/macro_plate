from . import common, docker
from .common import print_green


def init(context):
    """Create virtualhost in rabbitmq and grants permissions
    """
    print_green("Initial configuration for rabbitmq")
    docker.docker_compose_exec(
        context,
        'rabbitmq', 'rabbitmqctl add_vhost "macroplate-development"')  # noqa
    docker.docker_compose_exec(
        context,
        'rabbitmq', 'rabbitmqctl add_user macroplate_user manager')  # noqa
    docker.docker_compose_exec(
        context,
        'rabbitmq',
        'rabbitmqctl set_permissions -p "macroplate-development" macroplate_user ".*" ".*" ".*"')  # noqa
