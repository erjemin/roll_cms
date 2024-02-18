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
import socket
import os

if socket.gethostname() == 'seremin':
    # офисный комп (Windows)
    from roll_cms.my_secret_dev_office_win import *
elif socket.gethostname() == 'erjemin-home':
    # домашний комп (Windows)
    from roll_cms.my_secret_dev_home_win import *
elif socket.gethostname() in ['m1.N1', 'm1.local', ]:
    # домашний комп (MacOS)
    from roll_cms.my_secret_dev_home_mac import *
elif socket.gethostname() in ['orangepi5', 'vm678195', ]:
    # продакшн (боевой) сервер
    from roll_cms.my_secret_prod import *

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# Создайте пути внутри проекта следующим образом: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# ПРЕДУПРЕЖДЕНИЕ БЕЗОПАСНОСТИ: держите секретный production-ключ в секретом месте!
SECRET_KEY = MY_SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
# ПРЕДУПРЕЖДЕНИЕ БЕЗОПАСНОСТИ: не работайте в режиме DEBUG в production!
DEBUG = MY_DEBUG

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

    # 'easy_thumbnails.apps.EasyThumbnailsConfig',
    # 'filer.apps.FilerConfig',
    # 'mptt.apps.MpttConfig',

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
# TEMPLATES_DIR = BASE_DIR / 'templates-jinja2'

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
FIRST_DAY_OF_WEEK = 1                           # первый день недели: понедельник
SHORT_DATE_FORMAT = '%Y-%m-%d'
SHORT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# Security
# Останавливаем в http-заголовок 'X-Content-Type-Options: nosniff' для защиты от снифинга
# (запрет показа сайта в iframe на другом сайте)
SECURE_CONTENT_TYPE_NOSNIFF = True

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
MEDIA_ROOT = MY_MEDIA_ROOT
SITEMAP_ROOT = MY_SITEMAP_ROOT
STATICFILES_DIRS = [
    MY_STATIC_ROOT
]
# путь к каталогу static (в эту переменную использовать для указания пути где будут делаться кэш-картинки)
# STATIC_BASE_PATH = MY_STATIC_BASE_PATH_HOME2
DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.mysql",
        'HOST': MY_DATABASE_HOST,
        'PORT': MY_DATABASE_PORT,         # Set to "" for default. Not used with sqlite3.
        'NAME': MY_DATABASE_NAME,         # Not used with sqlite3.
        'USER': MY_DATABASE_USER,         # Not used with sqlite3.
        'PASSWORD': MY_DATABASE_PASSWORD,   # Not used with sqlite3.
        # 'OPTIONS': { 'autocommit': True, }
    }
}
TOUCH_RELOAD = MY_TOUCH_RELOAD

# Тип переменной для ключей primary key в моделях
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Настройки для кэширования
# https://docs.djangoproject.com/en/4.2/topics/cache/


# # ------------------- Настройки для django-filer -------------------
# # Настройки миниатюр THUMBNAIL (батарейка по созданию превьюшек)
# # Документацию см: https://easy-thumbnails.readthedocs.io/en/latest/ref/settings/
# if DEBUG:
#     THUMBNAIL_DEBUG = True
# else:
#     THUMBNAIL_DEBUG = False
# THUMBNAIL_DEFAULT_STORAGE = 'easy_thumbnails.storage.ThumbnailFileSystemStorage'    # Устанавливает класс,
#                                                                                     # для сохранения миниатюр.
# THUMBNAIL_NAMER = 'easy_thumbnails.namers.default'                  # Устанавливает класс, для генерации имен файлов.
# THUMBNAIL_SOURCE_GENERATORS = ('easy_thumbnails.source_generators.pil_image', )     # Устанавливает классы, для
#                                                                                     # генерации исходных изображений.
# THUMBNAIL_PROCESSORS = (
#     'easy_thumbnails.processors.colorspace',
#     'easy_thumbnails.processors.autocrop',
#     'easy_thumbnails.processors.scale_and_crop',
#     'easy_thumbnails.processors.filters',
#     'easy_thumbnails.processors.background',
# )
# # Определяем псевдонимы миниатюр THUMBNAIL
# #   size -- обязательный параметр, определяет границы, в которые должно вписываться сгенерированное изображение.
# #   quality -- число N — качество JPEG, целое число от 1 до 100. По умолчанию 85.
# #   subsampling -- число <N> устанавливает уровень субдискретизации цвета JPEG, где N:
# #     2 -- 4:1:1 (простые миниатюры, так и PIL по умолчанию)
# #     1 -- 4:2:2 (более четкие цветовые границы, небольшое увеличение размера файла)
# #     0 -- 4:4:4 (очень четкие цветовые границы, увеличение размера файла примерно на 15%).
# #    autocrop -- удаляет все ненужные пробелы с краев исходного изображения.
# #    bw -- преобразует изображение в оттенки серого.
# #    replace_alpha=#colorcode -- заменяет любой слой прозрачности сплошным цветом.
# #    crop=<smart|scale|W,H> -- обрезает края изображения, чтобы соответствовать соотношению сторон size
# #        перед изменением размера.
# #        smart -- изображение постепенно обрезается до запрошенного размера путем удаления
# #          фрагментов с краев с наименьшей энтропией.
# #        scale -- по крайней мере одно измерение соответствует заданным размерам.
# #        W,H -- изменяет поведение начала обрезки. Например: crop="0,0" -- будет обрезаться с левого и верхнего
# #          краев. crop="-10,-0" обрежет правый край (со смещением 10%) и нижний край. crop=",0" --
# #          сохранит поведение по умолчанию для оси x (горизонтальное центрирование изображения) и обрежет
# #          от верхнего края.
# THUMBNAIL_ALIASES = {
#     'cover': {
#         'x-small': {'size': (64, 64), 'autocrop': True},
#         'small': {'size': (180, 180), 'autocrop': True},
#         'preview': {'size': (340, 340), 'autocrop': True},
#         'standard': {'size': (680, 680), 'autocrop': True},
#         'big': {'size': (1140, 1140), 'autocrop': True},
#     },
# }
# THUMBNAIL_CACHE_DIMENSIONS = True   # Сохранять ли размеры миниатюр в базе данных (кеширование)
# THUMBNAIL_CHECK_CACHE_MISS = False  # Если размеры миниатюры не найдены в базе данных, то проверять наличие файла
# THUMBNAIL_DEFAULT_OPTIONS = {'subsampling': 1}      # Устанавливает параметры миниатюры по умолчанию.
# THUMBNAIL_PREFIX = 'thumbs_'                # Устанавливает префикс, используемый для создания файлов миниатюр.
# THUMBNAIL_EXTENSION = 'jpg'                 # Устанавливает расширение файла, используемое для миниатюр.
# THUMBNAIL_TRANSPARENCY_EXTENSION = 'png'    # Устанавливает расширение файла, используемое для миниатюр с прозрачностью.
# THUMBNAIL_QUALITY = 85                      # Устанавливает качество JPEG, целое число от 1 до 100. По умолчанию 85.
# THUMBNAIL_WIDGET_OPTIONS = {'size': (80, 80)}       # Устанавливает параметры миниатюры, используемые в виджете.
# THUMBNAIL_HIGHRES_INFIX = '_2x'     # Устанавливает инфикс, для различения эскизов для дисплеев Retina.
# THUMBNAIL_HIGH_RESOLUTION = True    # Включает миниатюры для дисплеев Retina.
# THUMBNAIL_PRESERVE_EXTENSIONS = ('png', 'gif')      # Устанавливает файлы, миниатюры которых не преобразуются в JPEG.
# THUMBNAIL_PROGRESSIVE = 600      # Порог размера (в px), после которого миниатюры будут progressive-jpeg (черезстрочные)



FILER_SUBJECT_LOCATION_IMAGE_DEBUG = True



