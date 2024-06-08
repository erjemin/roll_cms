# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from django import forms
from django.db import models
from django.forms import TextInput, Textarea
# from ckeditor.widgets import CKEditorWidget
# from codemirror import CodeMirrorTextarea
from roll_cms.models import TbTemplate, TbRoll, TbItem
# from web.add_function import safe_html_special_symbols
from roll_cms.settings import *
from roll_cms.add_function import safe_html_special_symbols, hyphenation_in_text
import roll_cms.EMT as EMT
import pytils
import random
import re

# Стилевые настройки для codemirror (единые для всех разделов админки)
cm_css = {'all': (
    '/static/codemirror-5.65.16/lib/codemirror.css',
    '/static/codemirror-5.65.16/addon/hint/show-hint.css',
    '/static/codemirror-5.65.16/addon/lint/lint.css',
    '/static/codemirror-5.65.16/theme/rubyblue.css',        # для темной темы
    '/static/codemirror-5.65.16/theme/solarized.css',       # для светлой темы
    )
}
# JavaScript-файлы для codemirror (единые для всех разделов админки)
cm_js = [
    '/static/codemirror-5.65.16/lib/codemirror.js',
    '/static/codemirror-5.65.16/mode/xml/xml.js',
    '/static/codemirror-5.65.16/mode/javascript/javascript.js',
    '/static/codemirror-5.65.16/mode/css/css.js',
    '/static/codemirror-5.65.16/mode/htmlmixed/htmlmixed.js',
    '/static/codemirror-5.65.16/mode/jinja2/jinja2.js',
    '/static/codemirror-5.65.16/mode/django/django.js',
    '/static/codemirror-5.65.16/addon/hint/xml-hint.js',
    '/static/codemirror-5.65.16/addon/hint/show-hint.js',
    '/static/codemirror-5.65.16/addon/lint/lint.js',
    '/static/codemirror-5.65.16/addon/lint/html-lint.js',
    '/static/codemirror-5.65.16/addon/lint/json-lint.js',
    '/static/codemirror-5.65.16/addon/lint/javascript-lint.js',
    '/static/codemirror-5.65.16/addon/lint/css-lint.js',
    '/static/codemirror-5.65.16/addon/mode/multiplex.js',
    '/static/codemirror-5.65.16/addon/mode/simple.js',
    '/static/codemirror-5.65.16/addon/mode/overlay.js',
    '/static/codemirror-5.65.16/addon/edit/closetag.js',
    '/static/codemirror-5.65.16/addon/runmode/colorize.js',
]

# ОПИСАНИЯ КЛАССОВ АДМИНКИ
# -- ШАБЛОНЫ {Т}
# -- Форма для админки шаблонов с подключением codemirror для редактирования шаблонов Django и Jinja2
class TemplateAdminForm(forms.ModelForm):
    class Meta:
        model = TbTemplate
        fields = '__all__'
        widgets = {
            'szJinjaCode': forms.Textarea(attrs={'class': 'code_editor'})
        }

# -- Админка шаблонов
@admin.register(TbTemplate)
class AdminTemplate(admin.ModelAdmin):
    class Media:
        # настройка подключения codemirror
        css = cm_css  # подключаемые CSS
        js = [        # Подключаемые JavaScript
            *cm_js,
            '/static/js/codemirror/set_theme.js',
            '/static/js/codemirror/init_cm_jinja.js',
        ]

    form = TemplateAdminForm  # подключение формы TemplateAdminForm
    search_fields = ['szFileName', 'szDescription', 'szJinjaCode']
    list_display = ('id', 'szFileName', 'szDescription', 'szVar')
    list_display_links = ('id', 'szFileName', 'szDescription',)
    empty_value_display = '<b style=\'color:red;\'>—//—</b>'
    actions_on_top = False
    actions_on_bottom = True

    def get_fields(self, request, obj=None):
        # Переопределяем способ получения полей из модели в форму админки.
        # Поле szJinjaCode у нас будет читаться из файла, а не из БД
        # Рецепт написал сам: https://qna.habr.com/q/1201124
        try:
            if obj.szFileName.lower().endswith(('.jinja2', '.j2', '.jinja',)):
                # это шаблон Jinja2, будем читать его из каталога шаблонов Jinja2
                path_filename = TEMPLATES[0]['DIRS'][0] / obj.szFileName
            else:
                # это какой-то другой шаблон, будем считать что это шаблон Django и его из каталога шаблонов Django
                path_filename = TEMPLATES[1]['DIRS'][0] / obj.szFileName
            with open(path_filename, "r", encoding='utf-8') as template:
                obj.szJinjaCode = template.read()
        except (AttributeError, FileNotFoundError, TypeError):
            pass
        return ['szFileName', 'szDescription', 'szJinjaCode', 'szVar']


# -- РОЛЛЫ [r]
# -- Форма для админки роллов с codemirror и дополнительными полями типографа и переносов
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
            'jRollOldSlugs': forms.Textarea(attrs={'class': 'json_editor1'}),
            'szRollTitle': forms.Textarea(attrs={'class': 'code_editor_title'}),
            'szRollText': forms.Textarea(attrs={'class': 'code_editor_text'}),
        }

    def clean(self):
        # Переопределим валидацию формы TbRoll-адмики и, заодно, переопределим значения некоторых полей.
        # Получаем данные из формы (поля формы)
        form_data: dict = super().clean()
        # ========== Обработка полей управляющих URL-слагами ==========
        if self.instance.pk is None or form_data['jRollOldSlugs'] is None:
            # если это новая запись или старых URL-слагов нет -- создадим список
            form_data['jRollOldSlugs'] = []
        if form_data['szRollSlug'] is None or re.sub(r"\s+", "", form_data['szRollSlug']) == "":
            # если в форме не указали URL-слаг, то создадим его из названия
            created_slug = pytils.translit.slugify(form_data['szRollName']).lower()
            # проверим уникальность созданного URL-слага
            while TbRoll.objects.filter(szRollSlug=created_slug).count() != 0:
                f"{created_slug[0:-3]}-{int(random.uniform(0, 255)):x}"
            form_data['szRollSlug'] = created_slug
        if self.instance.pk is not None and form_data['szRollSlug'] != TbRoll.objects.get(id=self.instance.pk).szRollSlug:
            # если это редактирование существующей записи и URL-слаг изменился, то добавим его в старые URL-слаги
            if TbRoll.objects.get(id=self.instance.pk).szRollSlug not in form_data['jRollOldSlugs']:
                form_data['jRollOldSlugs'].append(TbRoll.objects.get(id=self.instance.pk).szRollSlug)
            # если новый URL-слаг уже есть в старых URL-слагах, то удалим его из старых URL-слагов
            if form_data['szRollSlug'] in form_data['jRollOldSlugs']:
                form_data['jRollOldSlugs'].remove(form_data['szRollSlug'])
        # ========== Обработка полей управляющих типографом и переносами ==========

# -- Админка роллов
@admin.register(TbRoll)
class AdminRoll(admin.ModelAdmin):
    class Media:
        # настройка подключения codemirror
        css = cm_css  # подключаемые CSS
        js = [        # Подключаемые JavaScript
            *cm_js,
            '/static/js/codemirror/set_theme.js',
            '/static/js/codemirror/init_cm_json_1.js',
            '/static/js/codemirror/init_cm_title.js',
            '/static/js/codemirror/init_cm_text.js',
        ]

    # Переопределяем способ получения полей из модели в форму админки (чтобы получить фиктивные поля).
    def get_form(self, request, obj=None, **kwargs):
        return super().get_form(request, obj, **kwargs)

    # переопределяем метод сохранения модели
    def save_model(self, request, obj, form, change):
        # TODO: НЕ РАБОТАЕТ!! ПЕРЕНЕСТИ В RollAdminForm.clean() ... и улучшить
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

    form = RollAdminForm
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
            'fields': (('szRollSlug', 'szRollRedirectTo', ), 'jRollOldSlugs', ),
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


# -- Элементы <i>
# -- Форма для админки элементов с codemirror и дополнительными полями типографа и переносов
class ItemAdminForm(forms.ModelForm):
    # добавляем поле для типографа (поле фиктивное, его нет в модели и БД, но его обработка происходит в pre_save)
    class Meta:
        model = TbRoll
        fields = "__all__"
        widgets = {
            'jOldSlugs': forms.Textarea(attrs={'class': 'json_editor1'}),
            'jAtt': forms.Textarea(attrs={'class': 'json_editor2'}),
            'szTitle': forms.Textarea(attrs={'class': 'code_editor_title'}),
            'szNote': forms.Textarea(attrs={'class': 'code_editor_note'}),
            'szText': forms.Textarea(attrs={'class': 'code_editor_text'}),
        }


@admin.register(TbItem)
class AdminItem(admin.ModelAdmin):
    class Media:
        # настройка подключения codemirror
        css = cm_css  # подключаемые CSS
        js = [        # Подключаемые JavaScript
            *cm_js,
            '/static/js/codemirror/set_theme.js',
            '/static/js/codemirror/init_cm_json_1.js',
            '/static/js/codemirror/init_cm_json_2.js',
            '/static/js/codemirror/init_cm_title.js',
            '/static/js/codemirror/init_cm_note.js',
            '/static/js/codemirror/init_cm_text.js',
        ]

    # Переопределяем способ получения полей из модели в форму админки (чтобы получить фиктивные поля).
    def get_form(self, request, obj=None, **kwargs):
        return super().get_form(request, obj, **kwargs)

    form = ItemAdminForm
    list_display = ('id', 'szTitle', 'szSlug', 'iSort', 'tdStart', 'tdStop', 'bPublish')
    list_display_links = ('id', 'szTitle', 'szSlug')
    search_fields = ['szTitle', 'szNote', 'szText']
    list_editable = ('bPublish',)

