# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from django import forms
from django.db import models
from django.forms import TextInput, Textarea
# from ckeditor.widgets import CKEditorWidget
# from codemirror import CodeMirrorTextarea
from roll_cms.models import TbTemplate
# from web.add_function import safe_html_special_symbols
from roll_cms.settings import *

# from codemirror.widgets import CodeMirror

# class MyModelAdmin(admin.ModelAdmin):


# admin.site.register(MyModel, MyModelAdmin)


# ОПИСАНИЯ КЛАССОВ АДМИНКИ

class TemplateAdminForm(forms.ModelForm):
    # подключение codemirror для редактирования шаблонов Django и Jinja2 (для поля szJinjaCode в админке)
    # рецепт: https://webdevblog.ru/redaktirovanie-json-polej-cherez-django-adminku/
    # рецепт не работает для одновременной одсветки синтесиса нескольких языков
    # TODO: возможно стоит попробовать другие рецепты (через виждеты):
    # https://github.com/lambdalisue/django-codemirror-widget
    # https://github.com/onrik/django-codemirror
    # https://github.com/codemirror/codemirror5
    # https://codemirror.net/5/doc/manual.html

    class Meta:
        model = TbTemplate
        fields = "__all__"
        widgets = {
            'szJinjaCode': forms.Textarea(attrs={'class': 'code_editor'})
        }


class JsonAdminForm(forms.ModelForm):
    # подключение codemirror для редактирования json
    # рецепт: https://webdevblog.ru/redaktirovanie-json-polej-cherez-django-adminku/
    class Meta:
        model = TbTemplate
        fields = "__all__"
        widgets = {
            'data': forms.Textarea(attrs={'class': 'json-editor'}),
        }


# -- Управление шаблонами
@admin.register(TbTemplate)
class AdminTemplate(admin.ModelAdmin):
    class Media:
        # настройка подключения codemirror
        css = {
            'all': (
                # '/static/codemirror-5.65.13/doc/docs.css',
                '/static/codemirror-5.65.13/lib/codemirror.css',
                '/static/codemirror-5.65.13/addon/hint/show-hint.css',
                '/static/codemirror-5.65.13/addon/lint/lint.css',
                '/static/codemirror-5.65.13/theme/rubyblue.css',

            )
        }
        # для редактора json
        # js = (
        #     '/static/codemirror-5.65.13/lib/codemirror.js',
        #     # '/static/codemirror/formatting.js',
        #     '/static/codemirror-5.65.13/mode/javascript/javascript.js',
        #     '/static/codemirror-5.65.13/addon/lint/lint.js',
        #     '/static/codemirror-5.65.13/addon/lint/json-lint.js',
        #     '/static/js/codemirror/init_json.js'
        # )
        js = (
            '/static/codemirror-5.65.13/lib/codemirror.js',
            # '/static/codemirror-5.65.13/addon/hint/show-hint.js',
            # '/static/codemirror-5.65.13/addon/hint/xml-hint.js',
            # '/static/codemirror-5.65.13/addon/hint/html-hint.js',
            '/static/codemirror-5.65.13/addon/mode/multiplex.js',
            '/static/codemirror-5.65.13/addon/mode/overlay.js',
            '/static/codemirror-5.65.13/mode/xml/xml.js',
            # '/static/codemirror-5.65.13/mode/javascript/javascript.js',
            # '/static/codemirror-5.65.13/mode/css/css.js',
            '/static/codemirror-5.65.13/mode/htmlmixed/htmlmixed.js',
            '/static/codemirror-5.65.13/addon/lint/json-lint.js',
            # '/static/codemirror-5.65.13/mode/jinja2/jinja2.js',

            # '/static/codemirror-5.65.13/addon/runmode/colorize.js',
            # '/static/codemirror-5.65.13/addon/hint/html-hint.js',
            # '/static/codemirror-5.65.13/addon/lint/lint.js',
            # '/static/codemirror-5.65.13/addon/lint/html-lint.js',
            # '/static/codemirror/formatting.js',
            '/static/js/codemirror/init_jinja2.js'
            # '/static/js/codemirror/init_html.js'
        )
    form = TemplateAdminForm    # подключение формы TemplateAdminForm
    search_fields = ['szFileName', 'szDescription', 'szJinjaCode']
    list_display = ('id', 'szFileName', 'szDescription', 'szVar')
    list_display_links = ('id', 'szFileName', 'szDescription', )
    empty_value_display = '<b style=\'color:red;\'>—//—</b>'
    actions_on_top = False
    actions_on_bottom = True

    # Переопределяем способ получения полей из модели в форму админки.
    # Поле szJinjaCode у нас будет читаться из файла, а не из БД
    # Рецепт написал сам: https://qna.habr.com/q/1201124
    def get_fields(self, request, obj=None):
        try:
            with open(Path(TEMPLATES_DIR) / obj.szFileName, "r", encoding='utf-8') as template:
                obj.szJinjaCode = template.read()
        except (AttributeError, FileNotFoundError, TypeError):
            pass
        return ['szFileName', 'szDescription', 'szJinjaCode', 'szVar']


# admin.site.register(TbTemplate, AdminTemplate)
