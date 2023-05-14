# -*- coding: utf-8 -*-
"""
Code as config -- my_secret.py

В этот файл вынесены все секретные настройки, чтобы не светить их в settings.py
и иметь единую точку внесения изменений

Рекомендуется не светить этот файл в публичных git-репозиториях.
"""

# Хосты на которых может работать приложение
MY_ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '192.168.1.30',             # разработка домашний (Windows)
    '192.168.1.16',             # разработка домашний (MacOS)
    '10.10.5.6',                # разработка офис
    'rollcms.ru',               # продакшн
]

# Хостs на которых может работать приложение
MY_HOST_HOME1 = ['erjemin-home', ]      # разработка домашний (Windows)
MY_HOST_HOME2 = ['M1', 'm1.local', ]    # разработка домашний (MacOS)
MY_HOST_WORK = ['seremin', ]            # разработка офис (Windows)
MY_HOST_DEV = MY_HOST_HOME1 + MY_HOST_HOME2 + MY_HOST_WORK
MY_HOST_PROD = [
    'Z4',              # продакшн-тест z7.msk.rsvo.local)
    'vm2203242538',    # продакшн vds-хостинг masterhost
]

# SECURITY WARNING: keep the secret key used in production secret!
# ВНИМАНИЕ БЕЗОПАСНОСТИ: храните с секрете (не светите в публичных git-репозитория)
# секретный ключ для продакшн
MY_SECRET_KEY = 'django-insecure-cy_ha5(g+5c81qohzi7%d3z0=yr7h4x+4*m0%wg7^!ug3+)f$-'

# Настройки для сообщений об ошибках когда все упало и т.п.
MY_ADMINS = (
    ('S.Erjemin', 'erjemin@gmail.com'),
)

# НАСТРОЙКИ КАТАЛОГОВ И ПУТЕЙ ФАЛОВ
# путь к каталогу static (статика, для web-сервера nginx или apache)
MY_STATIC_ROOT_HOME1: str = 'M:\\cloud-mail.ru\\PRJ\\2023_roll_cms\\public\\static'
MY_STATIC_ROOT_HOME2: str = '/Users/e-serg/PRJ/2023_roll_cms/public/static'
MY_STATIC_ROOT_WORK: str = 'M:\\cloud-mail.ru\\PRJ\\2023_roll_cms\\public\\static'
MY_STATIC_ROOT_PROD: str = '/home/web/roll_cms/public/static'     # продакшн vds-хостинг masterhost/nic-ru

# путь к каталогу media  (статика, для web-сервера nginx или apache)
MY_MEDIA_ROOT_HOME1: str = 'M:\\cloud-mail.ru\\PRJ\\2023_roll_cms\\public\\media/'
MY_MEDIA_ROOT_HOME2: str = '/Users/e-serg/PRJ/2023_roll_cms/public/media/'
MY_MEDIA_ROOT_WORK: str = 'M:\\cloud-mail.ru\\PRJ\\2023_roll_cms\\public\\media/'
MY_MEDIA_ROOT_PROD: str = '/home/web/roll_cms/public/media/'        # продакшн vds-хостинг masterhost/nic-ru

# путь к каталогу в который будут помещаться sitemap.xml сайта
MY_SITEMAP_ROOT_HOME1: str = 'M:\\cloud-mail.ru\\PRJ\\2023_roll_cms\\public/'
MY_SITEMAP_ROOT_HOME2: str = '/Users/e-serg/PRJ/2023_roll_cms/public/'
MY_SITEMAP_ROOT_WORK: str = 'M:\\cloud-mail.ru\\PRJ\\2023_roll_cms\\public/'
MY_SITEMAP_ROOT_PROD: str = '/home/web/roll_cms/public/'            # продакшн vds-хостинг masterhost/nic-ru

# расположение touch-reload-файла для "передёргивания" uWSGI, необходимое при обновлении шаблонов
MY_TOUCH_RELOAD_HOME1: str = 'M:\\cloud-mail.ru\\PRJ\\2023_roll_cms\\logs\\touch-reload.txt'
MY_TOUCH_RELOAD_HOME2: str = '/Users/e-serg/PRJ/2023_roll_cms/logs/touch-reload.txt'
MY_TOUCH_RELOAD_WORK: str = 'M:\\cloud-mail.ru\\PRJ\\2023_roll_cms\\logs\\touch-reload.txt'
MY_TOUCH_RELOAD_PROD: str = '/home/web/oknardia-ru/logs/touch-reload.txt'

# расположение touch-reload-файла для "передёргивания" uWSGI
MY_TOUCH_RELOAD_DEV_HOME1 = 'M:\\cloud-mail.ru\\PRJ\\2023_roll_cms\\logs\\touch-reload.txt'
MY_TOUCH_RELOAD_DEV_HOME2 = '/Users/e-serg/PRJ/2023_roll_cms/logs/touch-reload.txt'
MY_TOUCH_RELOAD_DEV_WORK = 'M:\\cloud-mail.ru\\PRJ\\PRJ_RSVO_south\\logs\\touch-reload.txt'
MY_TOUCH_RELOAD_PROD = '/home/web/roll_cms/logs/touch-reload.txt'

# НАСТРОЙКИ ДЛЯ СИСТЕМЫ УПРАВЛЕНИЯ БАЗЫ ДАННЫХ (предполагается использование MariaDB)
# Хост
MY_DATABASE_HOST_HOME1: str = '10.10.5.30'
MY_DATABASE_HOST_HOME2: str = '192.168.1.16'
MY_DATABASE_HOST_WORK: str = '10.10.5.6'
MY_DATABASE_HOST_PROD: str = 'localhost'

# database
MY_DATABASE_NAME_HOME1: str = 'django_roll_cms'
MY_DATABASE_NAME_HOME2: str = 'django_roll_cms'
MY_DATABASE_NAME_WORK: str = 'django_roll_cms'
MY_DATABASE_NAME_PROD: str = 'django_roll_cms'

# port
MY_DATABASE_PORT_HOME1: str = '3307'
MY_DATABASE_PORT_HOME2: str = '3307'
MY_DATABASE_PORT_WORK: str = '3307'
MY_DATABASE_PORT_PROD: str = '3306'

# database user
MY_DATABASE_USER_HOME1: str = 'web'
MY_DATABASE_USER_HOME2: str = 'web'
MY_DATABASE_USER_WORK: str = 'web'
MY_DATABASE_USER_PROD: str = 'web'

# database password
MY_DATABASE_PASSWORD_HOME1: str = 'qwaseR12'
MY_DATABASE_PASSWORD_HOME2: str = 'qwaseR12'
MY_DATABASE_PASSWORD_WORK: str = 'qwaseR12'
MY_DATABASE_PASSWORD_PROD: str = '_STdra^&gonM'

# НАСТРОЙКИ ДЛЯ ПОЧТОВОГО СЕРВЕРА
MY_EMAIL: str = 'e@oknardia.ru'
MY_EMAIL_FROM: str = 'e@oknardia.ru'
MY_EMAIL_HOST_USER: str = 'info@oknardia.ru'                     # login
MY_EMAIL_HOST_PASSWORD: str = '8bZxFiVHqKcYWY8WpBfX)'        # password (создан как паспорт приложения mail.ru)
MY_EMAIL_PORT: int = 2525
MY_EMAIL_HOST: str = 'smtp.mail.ru'
