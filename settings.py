import dj_database_url

DEBUG = True
TEMPLATE_DEBUG = True

SECRET_KEY = 'this is my secret key'  # NOQA

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

DATABASES = {
    'default': dj_database_url.config(default='postgres:///localized_fields'),
}

DATABASES['default']['ENGINE'] = 'psqlextra.backend'

LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('en', 'English'),
    ('ro', 'Romanian'),
    ('nl', 'Dutch')
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'django.contrib.messages',
    'localized_fields',
    'tests',
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

MIDDLEWARE = [
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]

# set to a lower number than the default, since
# we want the tests to be fast, default is 100
LOCALIZED_FIELDS_MAX_RETRIES = 3

LOCALIZED_FIELDS_EXPERIMENTAL = False
