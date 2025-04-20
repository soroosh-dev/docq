# config/test.py
# Test settings

from .base import * #noqa
# Override settings for running tests

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('TEST_DB_NAME', default=''),
        'USER': config('TEST_DB_USER', default=''),
        'PASSWORD': config('TEST_DB_PASSWORD', default=''),
        'HOST': config('TEST_DB_HOST', default=''),
        'PORT': config('TEST_DB_PORT', default=''),
        'ATOMIC_REQUESTS': True
    }
}