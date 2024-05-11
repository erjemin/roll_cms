# -*- coding: utf-8 -*-
# ВСЕ СЕКРЕТНЫЕ НАСТРОЙКИ ПРОЕКТА ДЛЯ РАЗРАБОТКИ В ОФИСЕ (под Windows)
"""
В этот файл вынесены все секретные настройки, чтобы не светить их в settings.py
Например, при размещении в публичный репозиториях.
"""

MY_DEBUG = True

# Хосты на которых может работать приложение
MY_ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '192.168.1.2',     # ip 
    'you.site.com',    # domain
]


# Ключ Django
MY_SECRET_KEY = 'ваш_очень_сложный_секретный_ключ_для_приложения/сайта/проекта'

# Настройки для сообщений об ошибках когда все упало и т.п.
MY_ADMINS = (
    ('My.Person', 'your@admin.email'),   # имя и email админа
)

#########################################
# настройки для почтового сервера
MY_EMAIL = 'your@admin.email'
MY_EMAIL_FROM = 'your@admin.email'
MY_EMAIL_HOST = 'smtp.admin.email'                          # host разработка домашний
MY_EMAIL_HOST_USER = 'your@admin.email'                     # login-smtp (для публичных используйте пароли приложений)
MY_EMAIL_HOST_PASSWORD = 'очень_секретный_пароль_smtp'      # password-smtp
MY_EMAIL_PORT = 2525                                        # port-smtp
MY_EMAIL_USE_TLS = True

# Настройки подключения к БД MySQL
MY_DATABASE_HOST = '192.168.1.2'                     # db-host разработка домашний
MY_DATABASE_NAME = 'django_roll_cms'             # db-name разработка домашний
MY_DATABASE_PORT = '3306'
MY_DATABASE_USER = 'db_user'
MY_DATABASE_PASSWORD = 'db_password'

# Путь к файлу-метке для перезагрузки uwsgi
MY_TOUCH_RELOAD = '/home/user/web/roll-cms/logs/reload_roll_cms.txt'

# Пути к медиафайлам
MY_MEDIA_ROOT = '/home/user/web/roll-cms/public/media'

# Пути к статическим файлам
MY_STATIC_ROOT = '/home/user/web/roll-cms/public/static/'

# Путь к корню сайта (там где robots.txt, sitemap.xml, favicon.ico и т.п.)
MY_SITE_ROOT = '/home/user/web/roll-cms/public'

# Для django-filer
MY_FILER_PUBLIC_STORAGE_LOCATION = '/home/user/web/roll-cms/media/filer'
MY_FILER_PUBLIC_STORAGE_BASE_URL = '/media/_file_/'
MY_FILER_PUBLIC_STORAGE_UPLOAD_TO_PREFIX = 'filer_pub'
MY_FILER_PUBLIC_THUMBNAILS_LOCATION = '/home/user/web/roll-cms/media/filer_x/'
MY_FILER_PUBLIC_THUMBNAILS_BASE_URL = '/media/_file_s_/'
