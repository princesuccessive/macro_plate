# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
# default settings for mdillon/postgis image



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'postgres',
        'PORT': '5432',
    }
}

