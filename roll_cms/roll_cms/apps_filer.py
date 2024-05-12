# -*- coding: utf-8 -*-
# это "обертка" для приложения django-filer, чтобы можно было переопределить название приложения
from filer.apps import FilerConfig
from django.utils.translation import gettext_lazy


class MyFilerConfig(FilerConfig):
    verbose_name = gettext_lazy("Файлы и изображения")

# TODO: похоже сюда же можно будет переместить все специфичные для django-filer настройки
#  из settings.py. Надо будет поверить позже!
