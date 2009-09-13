DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ()
MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = ':memory:'
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

TIME_ZONE = 'UTC'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True

MEDIA_ROOT = ''
MEDIA_URL = ''
ADMIN_MEDIA_PREFIX = '/media/'

SECRET_KEY = '2edb!5x_fn19zdk!rq4_hkc&oq&qnbs@%=pk09l#z866nm_o%m'
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'examples.urls'

TEMPLATE_DIRS = ()

INSTALLED_APPS = (
    'django_safeform',
    'demoforms',
)

DEBUG_PROPAGATE_EXCEPTIONS = True # So we can see them from our test runner
