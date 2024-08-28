# -*- coding: utf-8 -*-
from jinja2 import lexer, nodes, Environment
from jinja2.ext import Extension
from django.urls import reverse
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils import timezone
from django.template.defaultfilters import date
from django.conf import settings
from datetime import datetime
from easy_thumbnails.templatetags.thumbnail import thumbnail_url
from easy_thumbnails.files import get_thumbnailer

def safe_thumbnail_url(url: str = "", alias: str = "") -> str:
    """ Возвращает "защищенный" URL-адрес миниатюры изображения, созданной с помощью easy-thumbnails.
        Если URL-адрес изображения отсутствует или алиас не найден, возвращает пустую строку.

    :param url: URL-адрес исходной картинки
    :param alias: Алиас миниатюры
    :return: URL-адрес миниатюры изображения
    """
    if not url:
        return str()  # Возвращаем пустую строку, если URL картинки отсутствует
    try:
        thumbnailer = get_thumbnailer(url)
        return thumbnailer[alias].url
    except KeyError:
        return str()  # Возвращаем пустую строку, если алиас не найден


# ОКРУЖЕНИЕ jinja2:
def environment(**options) -> Environment:
    """  Создает и возвращает объект окружения Jinja2 с настройками по умолчанию.

    :param options: Настройки для окружения Jinja2 (с распаковкой словаря)
    :return: Объект окружения Jinja2
    """
    env = Environment(**options)
    # добавляет тег static в jinja2 для обслуживания статики django
    # https://samuh.medium.com/using-jinja2-with-django-1-8-onwards-9c58fe1204dc
    env.globals.update({
        "static": staticfiles_storage.url,
        "url": reverse
    })

    # Добавляем функцию easy-thumbnails как Jinja2-фильтр
    # Рецепт: https://stackoverflow.com/a/35641120/1504067
    env.filters.update({
        'thumbnail_url': safe_thumbnail_url,
    })
    # env.filters['thumbnail_url'] = safe_thumbnail_url

    return env


# КЛАСС добавляет тег now в jinja2 (почти как в шаблонизаторе django)
# https://stackoverflow.com/a/51641667/1504067
class DjangoNow(Extension):
    tags = set(['now'])

    @staticmethod
    def _now(date_format):
        tz_info = timezone.get_current_timezone() if settings.USE_TZ else None
        formatted = date(datetime.now(tz=tz_info), date_format)
        return formatted

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        token = parser.stream.expect(lexer.TOKEN_STRING)
        date_format = nodes.Const(token.value)
        call = self.call_method('_now', [date_format], lineno=lineno)
        token = parser.stream.current
        if token.test('name:as'):
            next(parser.stream)
            as_var = parser.stream.expect(lexer.TOKEN_NAME)
            as_var = nodes.Name(as_var.value, 'store', lineno=as_var.lineno)
            return nodes.Assign(as_var, call, lineno=lineno)
        else:
            return nodes.Output([call], lineno=lineno)
