DEBUG = True
TEMPLATE_DEBUG = True

SECRET_KEY = 'this is my secret key'

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'localized_fields',
        'HOST': 'localhost'
    }
}

LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('en', 'English'),
    ('ro', 'Romanian'),
    ('nl', 'Dutch')
)

INSTALLED_APPS = [
    'localized_fields',
    'tests'
]
