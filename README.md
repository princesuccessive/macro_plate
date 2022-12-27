# README

## Generate actual docs with inv docs.sphinx after all instructions below

You have to have the following tools installed prior initalizing the project:

- [docker](https://docs.docker.com/engine/installation/)
- [docker-compose](https://docs.docker.com/v1.8/compose/install/)
- [invoke](https://github.com/pyinvoke/invoke/)
- [rancherssh](https://github.com/fangli/rancherssh)
- [pip-tools](https://github.com/jazzband/pip-tools)
- [pyenv](https://github.com/pyenv/pyenv)
- [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)
- [setuptools](https://github.com/pypa/setuptools)

## [Invoke usage commands](http://docs.pyinvoke.org/en/1.3/concepts/invoking-tasks.html#basic-command-line-layout)
Example calls:

Equivalent calls

```bash
inv tests.run --path=apps.users
inv tests.run --path apps.users
inv tests.run -p apps.users
```

For more than one flag

```bash
inv tests.run --path apps.users -p='--parallel --failfast'
```

If arguments is boolean

```bash
inv project.compile_requirements --u
```

to set the value to True

```bash
inv project.compile_requirements --no-u
```

to set the value to False


## Required linux packages

You also need to install sqlite3 (including develop package) so you can use
ipython properly

```bash
sudo dnf install sqlite
sudo dnf install sqlite-devel sqlite-tcl sqlite-jdbc
```

if you're on Ubuntu, then

```bash
sudo apt-get install sqlite3 libsqlite3-dev
```

## Build project and start coding

Also you should be logged in Saritasa docker registry, i.e. run
`docker login docker.saritasa.com` (use LDAP credentials), you need to
authenticate again docker.saritasa.com, so docker can pull images from our own
docker registry

Initialize project:

```bash
$ inv project.init
```

Run local server:

```bash
$ MACROPLATE_ENVIRONMENT=local fab django.run
```

or export environment variable once and run without variable

```bash
$ export MACROPLATE_ENVIRONMENT=local
$ inv django.run
```

If you work on documentation, run sphinx:

```bash
$ inv docs.sphinx
```

Once you run `project.init` initially you can start web server with
`inv django.run` command without executing `project.init` call.

## Local development

You can develop inside docker container, or using local python interpeter,
if you prefer local python, then create `.invoke` file in the root with the
following content

```
[Project]
interpreter = local
```

By default we assume you will develop inside docker container, but if you don't
want to use a Docker, just create virtualenv and then (once activated)

```bash
pip install -r requirements/development.txt
```

## Async celery

If you plan to develop and debug async tasks with celery, pls create virtualhost
inside rabbitmq container and grant user permissions as shown below

```bash
$ docker-compose run rabbitmq
$ docker-compose exec rabbitmq rabbitmqctl add_vhost "macroplate-development"
$ docker-compose exec rabbitmq rabbitmqctl add_user macroplate_user manager
$ docker-compose exec rabbitmq rabbitmqctl set_permissions -p "macroplate-development" macroplate_user ".*" ".*" ".*"
```

If however you started the development with `inv project.init` these
operations are already completed

You may need to adjust `CELERY` settings in `config/settings/development.py`
as needed

## CLI

There are bunch of commands available for your using `inv` command, just type
next command to list all available commands:

```bash
$ inv -l
```

Happy Coding!
