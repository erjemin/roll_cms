# -*- coding: utf-8 -*-
# ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ ПРОЕКТА ROLL_CMS (не вьшки)

from roll_cms.settings import *
from django.http import HttpRequest, HttpResponse


def check_cookies(request: HttpRequest) -> bool:
    # проверка, что посетитель согласился со сбором данных через cookies
    if request.COOKIES.get('cookie_accept'):
        return False
    return True


def safe_html_special_symbols(s: str) -> str:
    """ Очистка строки от HTML-разметки типографа

        :param s:   строка которую надо очистить
        :return: str:
    """
    # очистка строки от некоторых спец-символов HTML
    result = s.replace('&shy;', '­')
    result = result.replace('<span class="laquo">', '')
    result = result.replace('<span style="margin-right:0.44em;">', '')
    result = result.replace('<span style="margin-left:-0.44em;">', '')
    result = result.replace('<span class="raquo">', '')
    result = result.replace('<span class="point">', '')
    result = result.replace('<span class="thinsp">', ' ')
    result = result.replace('<span class="ensp">', '')
    result = result.replace('</span>', '')
    result = result.replace('&nbsp;', ' ')
    result = result.replace('&laquo;', '«')
    result = result.replace('&raquo;', '»')
    result = result.replace('&hellip;', '…')
    result = result.replace('<nobr>', '')
    result = result.replace('</nobr>', '')
    result = result.replace('&mdash;', '—')
    result = result.replace('&#8470;', '№')
    result = result.replace('<br />', ' ')
    result = result.replace('<br>', ' ')
    return result
