import django

if django.VERSION > (1, 2):
    DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
                }
    }
else:
    DATABASE_ENGINE = 'sqlite3'
    DATABASE_NAME = ':memory:'

INSTALLED_APPS = (
    'contextual.tests',
)
