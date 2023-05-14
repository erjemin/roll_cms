# -*- coding: utf-8 -*-
# ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ ПРОЕКТА ROLL_CMS (не вьшки)

from roll_cms.settings import *
from django.http import HttpRequest, HttpResponse


def check_cookies(request: HttpRequest) -> bool:
    # проверка, что посетитель согласился со сбором данных через cookies
    if request.COOKIES.get('cookie_accept'):
        return False
    return True
