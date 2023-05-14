# -*- coding: utf-8 -*-
"""
Конфигурация ASGI для проекта roll_cms.

Он предоставляет вызываемый ASGI как переменную уровня модуля с именем «приложение».

Дополнительные сведения об этом файле см. документацию:
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'roll_cms.settings')

application = get_asgi_application()
