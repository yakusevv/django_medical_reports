import os

from .secret_data import SECRET_KEY, TIME_ZONE
from .secret_data import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, ALLOWED_HOST


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', SECRET_KEY)

DEBUG = bool( os.environ.get('DJANGO_DEBUG', True) )

CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_BROWSER_XSS_FILTER = True

ALLOWED_HOSTS = [
                os.environ.get('ALLOWED_HOST', ALLOWED_HOST)
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'reports.apps.ReportsConfig',
    'blog.apps.BlogConfig',
    'profiles.apps.ProfilesConfig',
    'django_select2',
    'tempus_dominus',
    'crispy_forms',
]

#apps settings
TEMPUS_DOMINUS_LOCALIZE = True
#TEMPUS_DOMINUS_INCLUDE_ASSETS = False
CRISPY_TEMPLATE_PACK = 'bootstrap4'


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

ROOT_URLCONF = 'medical_reports.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
                os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'reports.context_processors.list_of_countries',
                'reports.context_processors.storage_information'
            ],
        },
    },
]

WSGI_APPLICATION = 'medical_reports.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE'  : 'django.db.backends.mysql',
        'NAME'    : os.environ.get('DB_NAME', DB_NAME),
        'USER'    : os.environ.get('DB_USER', DB_USER),
        'PASSWORD': os.environ.get('DB_PASSWORD', DB_PASSWORD),
        'HOST'    : os.environ.get('DB_HOST', DB_HOST),
        'PORT'    : os.environ.get('DB_PORT', DB_PORT),
        'OPTIONS' : {
            'autocommit': True,
            'charset': 'utf8'
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-US'

LANGUAGES = (
    ('en', 'English'),
    ('ru', 'Russian'),
)

USE_I18N = True

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

USE_L10N = True

USE_TZ = True

DATE_FORMAT = 'j E Y'

TIME_FORMAT = 'H:i'

DATETIME_FORMAT = 'j E Y H:i'

DATE_INPUT_FORMATS = [
    '%d/%m/%Y', '%Y/%m/%d',  # '25/10/2006', '2008/10/25'
    '%d-%m-%Y', '%Y-%m-%d',  # '25-10-2006', '2008-10-25'
    '%d-%m-%y', '%d/%m/%y',  # '25-10-06', '25/10/06'
]
DATETIME_INPUT_FORMATS = [
    '%d/%m/%Y %H:%M:%S',     # '25/10/2006 14:30:59'
    '%d/%m/%Y %H:%M:%S.%f',  # '25/10/2006 14:30:59.000200'
    '%d/%m/%Y %H:%M',        # '25/10/2006 14:30'
    '%d/%m/%Y',              # '25/10/2006'
    '%d/%m/%y %H:%M:%S',     # '25/10/06 14:30:59'
    '%d/%m/%y %H:%M:%S.%f',  # '25/10/06 14:30:59.000200'
    '%d/%m/%y %H:%M',        # '25/10/06 14:30'
    '%d/%m/%y',              # '25/10/06'
    '%Y-%m-%d %H:%M:%S',     # '2006-10-25 14:30:59'
    '%Y-%m-%d %H:%M:%S.%f',  # '2006-10-25 14:30:59.000200'
    '%Y-%m-%d %H:%M',        # '2006-10-25 14:30'
    '%Y-%m-%d',              # '2006-10-25'
    '%d-%m-%Y %H:%M:%S',     # '25-10-2006 14:30:59'
    '%d-%m-%Y %H:%M:%S.%f',  # '25-10-2006 14:30:59.000200'
    '%d-%m-%Y %H:%M',        # '25-10-2006 14:30'
    '%d-%m-%Y',              # '25-10-2006'
    '%d-%m-%y %H:%M:%S',     # '25-10-06 14:30:59'
    '%d-%m-%y %H:%M:%S.%f',  # '25-10-06 14:30:59.000200'
    '%d-%m-%y %H:%M',        # '25-10-06 14:30'
    '%d-%m-%y',              # '25-10-06'
]
DECIMAL_SEPARATOR = ','
THOUSAND_SEPARATOR = '.'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'assets'),
        ]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_FINDERS = (

'django.contrib.staticfiles.finders.FileSystemFinder',

'django.contrib.staticfiles.finders.AppDirectoriesFinder',

)


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_REDIRECT_URL = 'news_list_url'
LOGOUT_REDIRECT_URL = 'login'
