# -*- coding: utf-8 -*-
import random

from django.db import models
from django.utils.timezone import now
# from filer.fields.image import FilerFileField
# from ckeditor.fields import RichTextField
# from ckeditor_uploader.fields import RichTextUploadingField
from datetime import datetime
# from web.add_function import safe_html_special_symbols
from roll_cms.settings import *
import os
# import pytils
# import datetime
# import urllib3
import json


class TbTemplate(models.Model):
    """ Шаблоны """
    szFileName = models.CharField(
        # primary_key=True,  # первичный ключ
        default=".jinja2", db_index=True, unique=True,  # индекс и уникальность
        null=True, blank=True,
        max_length=100,
        verbose_name="Файл Шаблона",
        help_text="Имя файла шаблона (расширение .jinja2 или .html)<br/>"
                  "<b style='color:red'>ПОДУМАЙТЕ ПЕРЕД ТЕМ КАК ИЗМЕНЯТЬ!!</b>"
    )
    szJinjaCode = models.TextField(
        default='', null=True, blank=True,
        verbose_name='Шаблон',
        help_text='Код шаблона (jinja2)',
        # TODO: добавить виджет codemirror для jinja2
        # https://github.com/lambdalisue/django-codemirror-widget
        # https://github.com/onrik/django-codemirror
        # https://github.com/codemirror/codemirror5
        # https://codemirror.net/5/doc/manual.html
    )
    szDescription = models.CharField(max_length=100, verbose_name='Описание')
    szVar = models.CharField(
        max_length=16, default='var',
        null=True, blank=True,
        verbose_name='Переменная'
    )

    def __unicode__(self):
        return f"{self.szFileName}"

    def __str__(self):
        return self.__unicode__()

    # переопределяем save() для записи шаблонов не только в ДБ, но и в файл
    def save(self, *args, **kwargs):
        path_filename = TEMPLATES_DIR / self.szFileName
        # проверим, если нет каталога в котором нужно сохранить шаблон, то создадим его
        if not os.path.exists(os.path.dirname(path_filename)):
            os.makedirs(os.path.dirname(path_filename))
        with open(path_filename, "w+", encoding='utf-8') as tmplt_file:
            tmplt_file.write(self.szJinjaCode.replace('\r\n', '\n'))
        # # для продакшн нужно "дёрнуть" файл-touch_reload, чтобы uWSGI "щёлкнул"
        # # (или отключить кеширование шаблонов в Django)
        with open(TOUCH_RELOAD, 'a') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} --"
                    f" \"{self.szFileName}\" RELOAD\n")
        super(TbTemplate, self).save(*args, **kwargs)

    # переопределяем метод delete() (пока, не удаляется)
    def delete(self, *args, **kwargs):
        pass
        # TODO: может быть добавить переименование файлов шаблона и удаление записи его из базы...
        # super(TbTemplate, self).delete(*args, **kwargs)

    class Meta:
        verbose_name = '[…Шаблон] Ⓣ'
        verbose_name_plural = '[…Шаблоны] Ⓣ'
