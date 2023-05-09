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
MY_HOST_HOME2 = ['m1', 'local.m1', ]    # разработка домашний (MacOS)
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

# расположение touch-reload-файла для "передёргивания" uWSGI
MY_TOUCH_RELOAD_DEV_HOME1 = 'M:\\cloud-mail.ru\\PRJ\\2023_roll_cms\\logs\\touch-reload.txt'
MY_TOUCH_RELOAD_DEV_HOME2 = '/Users/e-serg/PRJ/2023_roll_cms/logs/touch-reload.txt'
MY_TOUCH_RELOAD_DEV_WORK = 'M:\\cloud-mail.ru\\PRJ\\PRJ_RSVO_south\\logs\\touch-reload.txt'
MY_TOUCH_RELOAD_PROD = '/home/web/roll_cms/logs/touch-reload.txt'
