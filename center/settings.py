"""
Django settings for sit_center project.

Generated by 'django-admin startproject' using Django 2.1.8.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import environ

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env()
env.read_env(os.path.join(BASE_DIR, '.env'))
print('The .env file has been loaded. See base.py for more information')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '775x_*4z(zm@j4g_+ooa=zld!t%lhatml68c@ag=)k7!(es96$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', False)

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'center.apps.CenterConfig',
    'social_core',
    'social_django',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'center.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ]  # ,
            # 'builtins': [
            #    'center.tags',
            # ]
        },
    },
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': './django_cache',
    }
}

AUTH_USER_MODEL = 'center.User'
# USER_FIELDS = (
#    'email',
#    'username',
#    'first_name',
#    'last_name',
#    'unti_id',
#    'leader_id',
# )

SSO_UNTI_URL = env("SSO_UNTI_URL")

SOCIAL_AUTH_UNTI_KEY = env("SOCIAL_AUTH_UNTI_KEY")
SOCIAL_AUTH_UNTI_SECRET = env("SOCIAL_AUTH_UNTI_SECRET")
SOCIAL_AUTH_UNTI_REDIRECT_URL = env("SOCIAL_AUTH_UNTI_REDIRECT_URL")

WSGI_APPLICATION = 'center.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    # 'default': {
    #    'ENGINE': 'django.db.backends.mysql',
    #    'USER': env("DB_USER"),
    #    'PASSWORD': env("DB_PASSWORD"),
    #    'HOST': env("DB_HOST"),
    #    'PORT': env("DB_PORT")
    # },
    'dwh-test': {
        'ENGINE': 'django.db.backends.mysql',
        'USER': env("DWH_TEST_USER"),
        'PASSWORD': env("DWH_TEST_PASSWORD"),
        'HOST': env("DWH_TEST_HOST"),
        'PORT': env("DWH_TEST_PORT")
    },
    'dwh': {
        'ENGINE': 'django.db.backends.mysql',
        'USER': env("DWH_USER"),
        'PASSWORD': env("DWH_PASSWORD"),
        'HOST': env("DWH_HOST"),
        'PORT': env("DWH_PORT")
    }
}

PAGE_CACHE_TIME = env.int("PAGE_CACHE_TIME", 60)

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
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

AUTHENTICATION_BACKENDS = (
    'center.auth.UNTIBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ASSISTANT_TAGS_NAME = ['assistant', 'island_assistant']

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
