# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class RollCmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'roll_cms'
    verbose_name = gettext_lazy("САЙТ")
