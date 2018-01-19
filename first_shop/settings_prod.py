DEBUG = False

ALLOWED_HOSTS = ['*']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'emarket_db',
        'USER': 'emarket',
        'PASSWORD': 'emarket1501',
        'HOST': 'localhost',
        'PORT': '',
    }
}

