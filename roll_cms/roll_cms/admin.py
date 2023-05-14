# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea
# from ckeditor.widgets import CKEditorWidget
from roll_cms.models import TbTemplate
# from web.add_function import safe_html_special_symbols
from roll_cms.settings import *


# ОПИСАНИЯ КЛАССОВ АДМИНКИ
# -- Управление шаблонами
class AdminTemplate(admin.ModelAdmin):
    search_fields = ['szFileName', 'szDescription', 'szJinjaCode']
    list_display = ('id', 'szFileName', 'szDescription', 'szVar')
    list_display_links = ('id', 'szFileName', 'szDescription', )
    empty_value_display = '<b style=\'color:red;\'>—//—</b>'
    actions_on_top = False
    actions_on_bottom = True

    # Переопределяем получение полей из модели в форму админки.
    # Поле szJinjaCode будет читаться из файла, а не из БД
    # Рецепт написал сам: https://qna.habr.com/q/1201124
    def get_fields(self, request, obj=None):
        try:
            with open(Path(TEMPLATES_DIR) / obj.szFileName, "r", encoding='utf-8') as template:
                obj.szJinjaCode = template.read()
        except (AttributeError, FileNotFoundError, TypeError):
            pass
        return ['szFileName', 'szDescription', 'szJinjaCode', 'szVar']


admin.site.register(TbTemplate, AdminTemplate)
