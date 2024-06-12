# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
from django.db import models
from django.forms import TextInput, Textarea
# from ckeditor.widgets import CKEditorWidget
# from codemirror import CodeMirrorTextarea
from roll_cms.models import TbTemplate, TbRoll, TbItem
from roll_cms.settings import *
from roll_cms.add_function import hyphenation_in_text, process_slug_fields
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


# -- Типограф (поля для всех моделей, где нужен типограф).
# ТОЛЬКО ФИКТИВНЫЕ-ПОЛЯ, КОТОРЫЕ НУЖНЫЕ ДЛЯ ТИПОГРАФИРОВАНИЯ
class TypografAdminForm(forms.ModelForm):
    def __init__(self, *args, typograf_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        if typograf_choices is not None:
            # если в форме переданы варианты для поля типографа 'typograf', то используем их
            self.fields['typograf'].choices = typograf_choices

    typograf = forms.ChoiceField(label='Типограф', required=False, initial=0,
                                 help_text='<div style=\'margin-right:6em;\'>Обработать через встроенный'
                                           '<a href="http://mdash.ru" target="_blank">Типограф Муравьёва 3.5</a></div>'
                                           '<small><b>ХОРОШИЙ ТИПОГРАФ НО ИНОГДА ГЛЮЧИТ!</b><br/>'
                                           '&laquo;приклеивает&raquo; союзы и числительные, поддерживает неразрывные'
                                           '<br/>конструкции, замена тире, очень <b>навороченная расстановка<br/>'
                                           'кавычек</b> (с горизонтальным смещением, как при книжной<br/>'
                                           'типографике, идеально для цитат и прямой речи), расставляет<br/>'
                                           'абзацы (кроме заголовков) и т.п.</small>')

    hang_punct = forms.ChoiceField(label='Висячая пунктуация', required=False, initial=False,
                                   choices=[(0, 'Выключена'), (1, 'C помощью встроенного CSS'), (2, 'C помощью Class')],
                                   help_text='Висячая пунктуация — это способ<br/>расположения кавычек и скобок<br/>'
                                             'при левостороннем выравнивании (флажком).')

    hyp = forms.ChoiceField(label='Переносы', required=False, initial='off',
                            choices=[(0, 'Выключены'), (15, 'Слова ≥ 14 символов'), (8, 'Слова ≥ 8 символов')],
                            help_text='<div style=\'margin-right:15em;\'>Включить автоматические переносы<br />'
                                      'русскоязычных слов по слогам)</div>')

    mnemo = forms.ChoiceField(label="Спец.символы", required=False, initial=2,
                              choices=[(1, 'Мнемокод'), (2, 'Юникод'), (3, 'Удалить странный мнемокод'),
                                       (4, 'Сделать <p> и <br> из CR и CRLF (\\n и \\n\\r)'),
                                       (5, 'Очистить от HTML и странного мнемокода'),],
                              help_text='Способ кодирования спецсимволов.<br /><small>'
                                        'Мнемокод: &amp;laquo; &amp;copy; &amp;raquo; &amp;hellip; — совместим</br>со'
                                        ' старыми браузерами; Юникод: « © » … — компактнее.</br>'
                                        '<b style=\'color:red;\'>Все удалить — так же удалит все переносы.</b></small>')

    class Meta:
        abstract = True


# -- РОЛЛЫ [r]
# -- Форма для админки роллов с codemirror и дополнительными полями типографа и переносов
class RollAdminForm(TypografAdminForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, typograf_choices=[(0, 'Выключен'), (1, 'Только заголовки'), (2, 'Только анонс'),
                                                  (3, 'Только текст'), (4, 'Заголовки и анонс'), (5, 'Заголовки и текст'),
                                                  (6, 'Анонс и текст'), (7, 'Всё')], **kwargs)

    def clean(self):
        # Переопределим валидацию формы TbRoll-адмики и, заодно, переопределим значения некоторых полей.
        # ========== Обработка полей управляющих URL-слагами ==========
        process_slug_fields(self, field_4_sz_slug='szRollSlug', field_4_js_old_slugs='jRollOldSlugs',
                            field_4_slug_make_from='szRollName', model=TbRoll)
        # ========== Обработка полей управляющих типографом и переносами ==========
        # Получаем данные из формы (поля формы)
        form_data: dict = super().clean()

    class Meta:
        model = TbRoll
        fields = "__all__"
        widgets = {
            'jRollOldSlugs': forms.Textarea(attrs={'class': 'json_editor1'}),
            'szRollTitle': forms.Textarea(attrs={'class': 'code_editor_title'}),
            'szRollText': forms.Textarea(attrs={'class': 'code_editor_text'}),
        }

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

        obj.save()

    form = RollAdminForm
    list_display = ('id', 'szRollName', 'kRollTemplate', 'kDefaultContentTemplate', 'iRollItemInPage',
                    'szRollSortRule', 'bRollPublish')
    list_display_links = ('id', 'szRollName')
    search_fields = ['szRollName', 'szRollTitle', 'szRollText']
    list_editable = ('bRollPublish',)
    list_filter = ('bRollPublish',)
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
            'fields': (('typograf', 'hang_punct',), ('hyp', 'mnemo',),),
            'classes': ('collapse',),
        }),
    ]
    empty_value_display = '<b style=\'color:red;\'>—//—</b>'
    actions_on_top = False
    actions_on_bottom = True


# -- Элементы <i>
# -- Форма для админки элементов с codemirror и дополнительными полями типографа и переносов
class ItemAdminForm(TypografAdminForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, typograf_choices=[(0, 'Выключен'), (1, 'Только заголовки'), (2, 'Только анонс'),
                                                  (3, 'Только текст'), (4, 'Заголовки и анонс'), (5, 'Заголовки и текст'),
                                                  (6, 'Анонс и текст'), (7, 'Всё')], **kwargs)

    def clean(self):
        # Переопределим валидацию формы TbItem-адмики и, заодно, переопределим значения некоторых полей.
        # ========== Обработка полей управляющих URL-слагами ==========
        process_slug_fields(self, field_4_sz_slug='szSlug', field_4_js_old_slugs='jOldSlugs',
                            field_4_slug_make_from='szTitle', model=TbItem)
        # ========== Обработка полей управляющих типографом и переносами ==========
        # Получаем данные из формы (поля формы)
        form_data: dict = super().clean()
        if form_data['typograf'] != 0:
            # если типограф включен, то типографируем
            # (0, 'Выключен'), (1, 'Только заголовки'), (2, 'Только анонс'),
            # (3, 'Только текст'), (4, 'Заголовки и анонс'), (5, 'Заголовки и текст'),
            # (6, 'Анонс и текст'), (7, 'Всё')
            # if form_data['typograf'] in [1, 4, 5, 7]:
            #     form_data['szTitle'] = EMT.EMTypograph(form_data['szTitle']).apply()
            pass

    class Meta:
        model = TbItem
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

    # Добавляем поле со списком роллов в которые включен элемент
    def roll_list(self, obj):
        return ", ".join([roll.szRollName for roll in obj.kRoll.all()])
    roll_list.short_description = 'Роллы'

    form = ItemAdminForm
    list_display = ('id', 'szTitle', 'roll_list', 'iSort', 'tdStart', 'bPublish')
    list_display_links = ('id', 'szTitle', 'roll_list')
    search_fields = ['szTitle', 'szNote', 'szText']
    list_editable = ('bPublish',)
    list_filter = ('bPublish', 'kRoll__szRollName',)
    # Настройка страницы редактирования
    fieldsets = [
        (None, {
            'fields': ('kRoll', 'bPublish',),
        }),
        ('ДАТА И СОРТИРОВКА', {
            'fields': (('tdStart', 'tdStop',), ('iSort',),),
            'classes': ('collapse',),
        }),
        ('ЭЛЕМЕНТ КОНТЕНТА (заголовок, картинка, анонс и т.д.)', {
            'fields': ('szTitle', 'kImg', 'szNote', 'szText',),
        }),
        ('ТИПОГРАФ И ПЕРЕНОСЫ', {
            'fields': (('typograf', 'hang_punct',), ('hyp', 'mnemo',),),
            'classes': ('collapse',),
        }),
        ('SLUG', {
            'fields': ('szSlug', 'jOldSlugs',),
            'classes': ('collapse',),
        }),
        ('SEO', {
            'fields': ('szSeoKeywords', 'szSeoDescription',),
            'classes': ('collapse',),
        }),
        ('СПЕЦ-ШАБЛОН', {
            'fields': ('kTemplate',),
            'classes': ('collapse',),
        }),
        ('АТРИБУТЫ и ТЕГИ', {
            'fields': ('jAtt',),
        }),
    ]
    empty_value_display = '<b style=\'color:red;\'>—//—</b>'
    actions_on_top = False
    actions_on_bottom = True

