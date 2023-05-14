# -*- coding: utf-8 -*-
"""
Конфигурация WSGI для проекта roll_cms.

Он предоставляет вызываемый WSGI как переменную уровня модуля с именем ``application``.

Дополнительные сведения об этом файле см. документацию:
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roll_cms.settings')

application = get_wsgi_application()
