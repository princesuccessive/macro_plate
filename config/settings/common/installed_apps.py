# Application definition
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    # 'cacheops',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'bootstrap_datepicker_plus',
    'crispy_forms',
    'django_celery_beat',
)

LOCAL_APPS = (
    'libs',
    'apps.core',
    'apps.macroplate',
    'apps.users',
)

INSTALLED_APPS += LOCAL_APPS
