import os

from invoke import task

from . import common, django, k8s

##############################################################################
# Data generation for database
##############################################################################

DB_DUMP_COMMAND = (
    "PGPASSWORD=${DB_PASSWORD} "
    "pg_dump "
    "--no-owner "
    "--dbname=${DB_NAME} "
    "--host=${DB_HOST} "
    "--port=${DB_PORT} "
    "--username=${DB_USER} "
    "--file ${DUMP_FILE}.sql"
)
REMOTE_DB_DUMP_COMMAND = (
    "pg_dump "
    "--no-owner "
    "--dbname={DB_NAME} "
    "--host={DB_HOST} "
    "--port={DB_PORT} "
    "--username={DB_USER} "
    "--file {DUMP_FILE}.sql"
)
DB_LOAD_COMMAND = (
    "PGPASSWORD=${DB_PASSWORD} "
    "psql "
    "--quiet "
    "--dbname=${DB_NAME} "
    "--host=${DB_HOST} "
    "--port=${DB_PORT} "
    "--username=${DB_USER} "
    "--file ${DUMP_FILE}.sql"
)


@task
def backup_remote_db(context):
    """Create and get remote db dump."""
    common.print_green("Creating backup of remote db.")
    db_config = _get_remote_db_config(context)
    db_config.update(DUMP_FILE=f"/tmp/{k8s.NAMESPACE}_db_dump")
    command = REMOTE_DB_DUMP_COMMAND.format(**db_config)
    k8s.postgres_create_dump(
        context,
        command=command,
        password=db_config["DB_PASSWORD"],
    )
    k8s.postgres_get_dump(context)


@task
def backup_local_db(context):
    """Back up local db."""
    common.print_green("Creating backup of local db.")
    db_config = _get_local_db_config()
    db_config.update(DUMP_FILE="local_db_dump")
    context.run(command=DB_DUMP_COMMAND, env=db_config)


@task
def load_db_dump(context, file="local_db_dump"):
    """Load db dump to local db."""
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.local"
    common.print_green("Resetting local db")
    django.resetdb(context, apply_migrations=False)
    db_config = _get_local_db_config()
    db_config.update(DUMP_FILE=file)
    context.run(DB_LOAD_COMMAND, env=db_config)
    common.print_green("DB is ready for use")


def _get_local_db_config() -> dict:
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.local"
    from django.conf import settings
    db_settings = settings.DATABASES["default"]
    return dict(
        DB_HOST=db_settings["HOST"],
        DB_NAME=db_settings["NAME"],
        DB_PASSWORD=db_settings["PASSWORD"],
        DB_PORT=str(db_settings["PORT"]),
        DB_USER=db_settings["USER"],
    )


def _get_remote_db_config(context) -> dict:
    config_data = k8s.get_remote_config(context)
    config_path = "config/settings/tmp.py"
    with open(config_path, "w", encoding="UTF-8") as file:
        file.write(config_data)
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.tmp"
    from django.conf import settings
    db_settings = settings.DATABASES["default"]
    settings = dict(
        DB_HOST=db_settings["HOST"],
        DB_NAME=db_settings["NAME"],
        DB_PASSWORD=db_settings["PASSWORD"],
        DB_PORT=str(db_settings["PORT"]),
        DB_USER=db_settings["USER"],
    )
    context.run(f"rm {config_path}")
    return settings


@task
def load_fixtures(context, fixtures=None):
    """Load fixtures to database

    Examples:
        # load specified fixtures
        inv data.load_fixtures --fixtures='users.json,clients.json'

    """
    common.print_green("Load fixtures")
    fixture_folder = '.dev/fixtures'
    order_file = os.path.join(fixture_folder, '.fixtures-order')
    fixtures = []
    if fixtures:
        fixtures = fixtures.split(',')
    else:
        with open(order_file) as order:
            fixtures = [os.path.join(fixture_folder, fixture)
                        for fixture in map(str.strip, order)
                        if fixture and not fixture.startswith('#')]
    for fixture in fixtures:
        django.manage(context, ' '.join(['loaddata', fixture]))
