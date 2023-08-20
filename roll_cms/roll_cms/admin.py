# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from django import forms
from django.db import models
from django.forms import TextInput, Textarea
# from ckeditor.widgets import CKEditorWidget
# from codemirror import CodeMirrorTextarea
from roll_cms.models import TbTemplate, TbRoll
# from web.add_function import safe_html_special_symbols
from roll_cms.settings import *
from roll_cms.add_function import safe_html_special_symbols, hyphenation_in_text
import roll_cms.EMT as EMT
import pytils
import random

# from codemirror.widgets import CodeMirror

# class MyModelAdmin(admin.ModelAdmin):


# admin.site.register(MyModel, MyModelAdmin)


# ОПИСАНИЯ КЛАССОВ АДМИНКИ

class TemplateAdminForm(forms.ModelForm):
    # подключение codemirror для редактирования шаблонов Django и Jinja2 (для поля szJinjaCode в админке)
    # рецепт: https://webdevblog.ru/redaktirovanie-json-polej-cherez-django-adminku/
    # рецепт не работает для одновременной подсветки синтаксиса нескольких языков
    # TODO: возможно стоит попробовать другие рецепты (через видждеты), но вряд-ли поможет:
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

    def get_fields(self, request, obj=None):
        # Переопределяем способ получения полей из модели в форму админки.
        # Поле szJinjaCode у нас будет читаться из файла, а не из БД
        # Рецепт написал сам: https://qna.habr.com/q/1201124
        try:
            with open(Path(TEMPLATES_DIR) / obj.szFileName, "r", encoding='utf-8') as template:
                obj.szJinjaCode = template.read()
        except (AttributeError, FileNotFoundError, TypeError):
            pass
        return ['szFileName', 'szDescription', 'szJinjaCode', 'szVar']


# -- Управление роллами
class RollAdminForm(forms.ModelForm):
    # добавляем поле для типографа (поле фиктивное, его нет в модели и БД, но его обработка происходит в pre_save)
    typograf = forms.BooleanField(label='Типограф', required=False, initial=False,
                                  help_text='Обработать через встроенный <a href="http://mdash.ru" target="_blank">'
                                            'Типограф Муравьёва 3.5</a><br />'
                                            '<small><b>ХОРОШИЙ ТИПОГРАФ, ИНОГДА ДАЖЕ СЛИШКОМ. '
                                            'ИНОГДА ГЛЮЧИТ! ПРОВЕРЯЙТЕ РЕЗУЛЬТАТ!!</b><br />'
                                            '&laquo;приклеивает&raquo; союзы и числительные, поддерживает неразрывные'
                                            'конструкции, замена тире, очень <b>навороченная расстановка кавы&shy;'
                                            'чек</b> (с горизонтальным смещением, как при книжной типографике,'
                                            'идеально для цитат и прямой речи), расставляет абзацы (кроме '
                                            'заголовков) и т.п.</small>')
    hyphenation = forms.BooleanField(label='Переносы', required=False, initial=False,
                                     help_text='Включить автоматические переносы    <br />'
                                               'русскоязычных слов по слогам<br /><small>'
                                               'В словах с расставленными переносами<br />'
                                               '(повторно) не работает</small>')
    hyphenation_len = forms.IntegerField(label='Длина слова', required=False, initial=14,
                                         help_text='Минимальная длина слова<br />'
                                                   'для переноса. <small>Переносы расстав-<br />'
                                                   'ляются только в словах длиннее</small>.')
    use_shy_for_hyphenation = forms.BooleanField(label='Использовать &shy;', required=False, initial=False,
                                                 help_text='Использовать &amp;shy;<br />'
                                                           '<small>Иначе через юникод-символ</small>')

    class Meta:
        model = TbRoll
        fields = "__all__"
        widgets = {
            'szRollText': forms.Textarea(attrs={'class': 'code_editor'}),
            'szRollTitle': forms.Textarea(attrs={'class': 'code_editor'}),
        }


@admin.register(TbRoll)
class AdminRoll(admin.ModelAdmin):
    class Media:
        # настройка подключения codemirror
        css = {
            'all': ('/static/codemirror-5.65.13/lib/codemirror.css',
                    '/static/codemirror-5.65.13/addon/hint/show-hint.css',
                    '/static/codemirror-5.65.13/addon/lint/lint.css',
                    '/static/codemirror-5.65.13/theme/rubyblue.css', )
        }
        js = (
            '/static/codemirror-5.65.13/lib/codemirror.js',
            '/static/codemirror-5.65.13/addon/mode/multiplex.js',
            '/static/codemirror-5.65.13/addon/mode/overlay.js',
            '/static/codemirror-5.65.13/mode/xml/xml.js',
            '/static/codemirror-5.65.13/mode/htmlmixed/htmlmixed.js',
            '/static/js/codemirror/init_html.js',
            '/static/codemirror-5.65.13/addon/hint/show-hint.js',
        )

    form = RollAdminForm

    # Переопределяем способ получения полей из модели в форму админки (чтобы получить фиктивные поля).
    def get_form(self, request, obj=None, **kwargs):
        return super().get_form(request, obj, **kwargs)

    # переопределяем метод сохранения модели
    def save_model(self, request, obj, form, change):
        # Проверяем необходимость расстановки переносов и расставляем
        try:
            if form.cleaned_data['hyphenation'] and int(form.cleaned_data['hyphenation_len']) > 6:
                # если нажата галочка "Переносы"
                obj.szRollTitle = hyphenation_in_text(obj.szRollTitle, int(form.cleaned_data["hyphenation_len"]))
                if form.cleaned_data['use_shy_for_hyphenation']:
                    obj.szRollTitle = obj.szRollTitle.replace('­', '&shy;')
                else:
                    obj.szRollTitle = obj.szRollTitle.replace('&shy;', '­')
                obj.szRollText = hyphenation_in_text(obj.szRollText, int(form.cleaned_data["hyphenation_len"]))
                if form.cleaned_data['use_shy_for_hyphenation']:
                    obj.szRollText = obj.szRollText.replace('­', '&shy;')
                else:
                    obj.szRollText = obj.szRollText.replace('&shy;', '­')
        except (KeyError, TypeError, ValueError):
            pass

        # Проверяем включен ли типограф и типографируем
        try:
            if form.cleaned_data['typograf']:
                # если нажата галочка "Типограф", то типографируем
                # https://habr.com/ru/articles/303608/
                # https://github.com/f213/richtypo.py и https://pypi.org/project/richtypo/
                # https://maks.live/articles/python/eto-tipograf/

                emt_title = EMT.EMTypograph()
                emt_title.setup({'Text.paragraphs': 'off'})
                emt_title.set_text(obj.szRollTitle)
                obj.szRollTitle = emt_title.apply()
                emt_roll_text = EMT.EMTypograph()
                emt_roll_text.setup({'Text.paragraphs': 'off'})
                emt_roll_text.set_text(obj.szRollText)
                emt_roll_text.set_tag_layout(layout=EMT.LAYOUT_STYLE)
                obj.szRollText = emt_roll_text.apply()
        except KeyError:
            pass

        # Проверяем наличие URL-слага и его уникальность
        if obj.szRollSlug is None or obj.szRollSlug == "" or " " in obj.szRollSlug:
            result_slug = pytils.translit.slugify(
                safe_html_special_symbols(obj.szRollName)
            ).lower()
            while TbRoll.objects.filter(szRollSlug=result_slug).count() != 0:
                f"{result_slug[0:-3]}-{int(random.uniform(0, 255)):x}"
            obj.szRollSlug = result_slug
        obj.save()

    formfield_overrides = {models.TextField: {'widget': forms.Textarea(attrs={'class': 'code_editor'})}}
    list_display = ('id', 'szRollName', 'kRollTemplate', 'kDefaultContentTemplate', 'iRollItemInPage',
                    'szRollSortRule', 'bRollPublish')
    list_display_links = ('id', 'szRollName')
    search_fields = ['szRollName', 'szRollTitle', 'szRollText']
    list_editable = ('bRollPublish',)


    # Настройка страницы редактирования
    fieldsets = [
        (None, {
            'fields': ('bRollPublish', 'szRollName', ),
        }),
        ('SLUG & REDIRECT', {
            'fields': ('szRollSlug', 'szRollRedirectTo', ),
            'classes': ('collapse',),
        }),
        ('ШАБЛОНЫ', {
            'fields': (('kRollTemplate', 'kDefaultContentTemplate', ),),
        }),
        ('СОРТИРОВКА, ФИЛЬТРАЦИЯ и ПАГИНАЦИЯ', {
            'fields': ('szRollSortRule', 'szRollFilterRule', 'iRollItemInPage',),
            'classes': ('collapse',),
        }),
        ('РОЛЛ (заголовок, картинка, вводный текст)', {
            'fields': ('szRollTitle', 'kRollImgPreview', 'szRollText',),
        }),
        ('ТИПОГРАФ И ПЕРЕНОСЫ', {
            'fields': ('typograf', ('hyphenation', 'hyphenation_len', 'use_shy_for_hyphenation'),),
            'classes': ('collapse',),
        }),
    ]
    empty_value_display = '<b style=\'color:red;\'>—//—</b>'
    actions_on_top = False
    actions_on_bottom = True


# admin.site.register(TbTemplate, AdminTemplate)
