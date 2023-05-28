# -*- coding: utf-8 -*-
"""
Django-настройки для проекта roll_cms.

Сгенерировано «django-admin startproject» с использованием Django 4.2.1.

Дополнительные сведения об этом файле см. документацию:
https://docs.djangoproject.com/en/4.2/topics/settings/

Полный список настроек и их значений см. документацию:
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
from pathlib import Path
from roll_cms._my_secret import *
import socket
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# Создайте пути внутри проекта следующим образом: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# ПРЕДУПРЕЖДЕНИЕ БЕЗОПАСНОСТИ: держите секретный ключ продакшна в секретом месте!
SECRET_KEY = MY_SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
# ПРЕДУПРЕЖДЕНИЕ БЕЗОПАСНОСТИ: не работайте в режиме DEBUG в продашене!
if socket.gethostname() in MY_HOST_DEV:
    DEBUG = True
else:
    # Все остальные gethostname (подразумевается продакшн)
    DEBUG = False

# Хосты на которых может работать приложение
ALLOWED_HOSTS = MY_ALLOWED_HOSTS


# Application definition (Определение приложений)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 'codemirror',   # виджет для редактора кода в админке

    'roll_cms.apps.RollCmsConfig',
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

ROOT_URLCONF = 'roll_cms.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [BASE_DIR / 'templates-jinja2', ],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'roll_cms.my_jinja2_addon.environment',
            'extensions': [
                'roll_cms.my_jinja2_addon.DjangoNow',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },  {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates-django', ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
TEMPLATES_DIR = BASE_DIR / 'templates-jinja2'

WSGI_APPLICATION = 'roll_cms.wsgi.application'

# Password validation (Проверка пароля)
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# Internationalization  (Интернационализация)
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True
FIRST_DAY_OF_WEEK = 1                           # 1'st day week -- monday
SHORT_DATE_FORMAT = '%Y-%m-%d'
SHORT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# НАСТРОЙКИ ДЛЯ ПОЧТОВОГО СЕРВЕРА (они одинаковые для DEV и PROD)
EMAIL_HOST = MY_EMAIL_HOST
EMAIL_PORT = MY_EMAIL_PORT
EMAIL_HOST_USER = MY_EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = MY_EMAIL_HOST_PASSWORD
SERVER_EMAIL = DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_USE_TLS = True
EMAIL_SUBJECT_PREFIX = 'ROLL_CMS ERR: '         # префикс для оповещений об ошибках и необработанных исключениях


# Статические файлы (CSS, JavaScript и служебные картинки) и медиа-файлы (загружаемые пользователем)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = 'media/'

# Настройки в зависимости от условий запуска проекта. В режиме разработки (DEBUG=True) могут использоваться
# различные компьютеры (отличаются через hostname) и соответвенно для каждого будут различные параметры
# подключения к базе данных, различные каталоги расположения статических- и медиа-файлов. и т.п.
if DEBUG and socket.gethostname() in MY_HOST_HOME1:
    # Разработка: Домашний компьютер под Windows
    pass
elif DEBUG and socket.gethostname() in MY_HOST_HOME2:
    #  Разработка: Домашний компьютер под MacOS
    MEDIA_ROOT = MY_MEDIA_ROOT_HOME2
    SITEMAP_ROOT = MY_SITEMAP_ROOT_HOME2
    STATICFILES_DIRS = [
        MY_STATIC_ROOT_HOME2,
    ]
    # путь к каталогу static (в эту переменную использовать для указания пути где будут делаться кэш-картинки)
    # STATIC_BASE_PATH = MY_STATIC_BASE_PATH_HOME2
    DATABASES = {
        'default': {
            'ENGINE': "django.db.backends.mysql",
            'HOST': MY_DATABASE_HOST_HOME2,
            'PORT': MY_DATABASE_PORT_HOME2,         # Set to "" for default. Not used with sqlite3.
            'NAME': MY_DATABASE_NAME_HOME2,         # Not used with sqlite3.
            'USER': MY_DATABASE_USER_HOME2,         # Not used with sqlite3.
            'PASSWORD': MY_DATABASE_PASSWORD_HOME2,   # Not used with sqlite3.
            # 'OPTIONS': { 'autocommit': True, }
        }
    }
    TOUCH_RELOAD = MY_TOUCH_RELOAD_DEV_HOME2
elif DEBUG and socket.gethostname() in MY_HOST_WORK:
    # Разработка: Офисный компьютер под Windows
    print('Разработка: Офисный компьютер под Windows')
    MEDIA_ROOT = MY_MEDIA_ROOT_WORK
    SITEMAP_ROOT = MY_SITEMAP_ROOT_WORK
    STATICFILES_DIRS = [
        MY_STATIC_ROOT_WORK,
    ]
    # путь к каталогу static (в эту переменную использовать для указания пути где будут делаться кэш-картинки)
    # STATIC_BASE_PATH = MY_STATIC_BASE_PATH_WORK
    DATABASES = {
        'default': {
            'ENGINE': "django.db.backends.mysql",
            'HOST': MY_DATABASE_HOST_WORK,
            'PORT': MY_DATABASE_PORT_WORK,  # Set to "" for default. Not used with sqlite3.
            'NAME': MY_DATABASE_NAME_WORK,  # Not used with sqlite3.
            'USER': MY_DATABASE_USER_WORK,  # Not used with sqlite3.
            'PASSWORD': MY_DATABASE_PASSWORD_WORK,  # Not used with sqlite3.
            # 'OPTIONS': { 'autocommit': True, }
        }
    }
    TOUCH_RELOAD = MY_TOUCH_RELOAD_DEV_WORK
else:
    # Продакшн: режим DEBUG отключен или неизвестный хостнейм
    pass

# Настройки для работы с виджетом CodeMirror
# CODEMIRROR_PATH = STATIC_URL + 'js/codemirror/'

# Тип переменной для ключей primary key в моделях
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

