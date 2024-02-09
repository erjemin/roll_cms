# -*- coding: utf-8 -*-
import random

from django.db import models
from django.utils.timezone import now
# from filer.fields.image import FilerFileField
# from ckeditor.fields import RichTextField
# from ckeditor_uploader.fields import RichTextUploadingField
from datetime import datetime
from roll_cms.add_function import safe_html_special_symbols
from roll_cms.settings import *
import os
import pytils
# import datetime
# import urllib3
import json


class TbTemplate(models.Model):
    """ Шаблоны. Таблица в БД `roll_cms_tbtemplate` """
    # --------------+----------------------------------+--------------+------+---------+----------------+
    # поле          | Назначние                        | тип          | NULL | DEFAULT | Extra          |
    # --------------+----------------------------------+--------------+------+---------+----------------+
    # id            | первичный ключ                   | bigint(20)   | NO   | NULL    | auto_increment |
    # szFileName    | имя файла шаблона                | varchar(100) | YES  | ''      | unique         |
    # szJinjaCode   | код шаблона                      | longtext     | YES  | ''      |                |
    # szDescription | назначение/описание шаблона      | varchar(100) | YES  | ''      |                |
    # szVar         | переменная для передачи значений | varchar(16)  | YES  | 'var'   |                |
    # --------------+----------------------------------+--------------+------+---------+----------------+
    szFileName = models.CharField(
        # primary_key=True,  # первичный ключ
        default=".jinja2", db_index=True, unique=True,  # индекс и уникальность
        null=True, blank=True,
        max_length=100,
        verbose_name="Файл Шаблона",
        help_text="Имя файла шаблона (расширение .jinja2 или .html)<br/>"
                  "<b style='color:red'>ПОДУМАЙТЕ ПЕРЕД ТЕМ КАК ИЗМЕНЯТЬ!!</b>",
    )
    szJinjaCode = models.TextField(
        default='', null=True, blank=True,
        verbose_name='Шаблон',
        help_text='Код шаблона (jinja2)',
    )
    szDescription = models.CharField(
        max_length=100,
        default='', null=True, blank=True,
        verbose_name='Описание',
        help_text='Назначение/описание шаблона',
    )
    szVar = models.CharField(
        max_length=16, default='var',
        null=True, blank=True,
        verbose_name='Переменная',
        help_text='Переменная через которую этот шаблон принимает данные',
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


# class TbRoll(models.Model):
#     """ Роллы. Они объединяют однородные по представлению сущности (ленты новостей, блоги, фотоальбомы,
#     баннеры, товары и т.д.). Таблица в БД `roll_cms_tbroll` """
#     # ============================================================
#     # ТАБЛИЦА TbBlock (КАТЕГОРИИ КОНТЕНТА)
#     # ------------------------------------------------------------
#     # | id                         -- id | primarykey bigint | autoincrement |
#     # | szRollSlug                 -- URL-слаг | VARCHAR(155) | UNIQUE |
#     # | szRollName                 -- имя ролла | VARCHAR(64) | UNIQUE |
#     # | bRollPublished             -- опубликован | TINYINT(1) | DEFAULT 1 |
#     # | kRollTemplate_id           -- шаблон для отображения ролла | foreignkey bigint |
#     # | kDefaultContentTemplate_id -- шаблон для отображения контента | foreignkey bigint |
#     # | iRollItemInPage            -- число единиц контента на одной странице ролла | SMALLINT UNSIGNED | DEFAULT 10 |
#     # | szRollSortRule             -- правило сортировки | VARCHAR(64) | DEFAULT '-dtCreate' |
#     # | szRollFilterRule           -- правило фильтрации | VARCHAR(64) | DEFAULT 'bPublish=True' |
#     # | szRollTitle                -- заголовок ролла | VARCHAR(255) |
#     # | kRollImgPreview_id         -- превью ролла | foreignkey int |
#     # | szRollText                 -- текст ролла | TEXT |
#     # | szRollRedirectTo           -- перенаправление ролла | VARCHAR(500) |
#     # | dtRollCreate               -- дата создания ролла | DATETIME(6) | DEFAULT NOW() |
#     # | dtRollTimeStamp            -- штамп времени (дата изменения ролла) | DATETIME(6) | DEFAULT NOW() |
#     # ============================================================
#     szRollSlug = models.SlugField(
#         default="", max_length=155, blank=True, null=True, db_index=True, unique=True,
#         verbose_name="URL-слаг",
#         help_text="URL-слаг страницы… 155 символа (пробелы заменяются '-').<br/>"
#                   "<small><b>Если оставить пустым, то URL-слаг сформируется автоматически</b></small>"
#     )
#     szRollName = models.CharField(
#         max_length=64, blank=False, null=False,
#         verbose_name="Имя ролла (техническое)",
#         help_text="Техническое название ролла (наименование категории, раздела, сборника)<br/>"
#                   "для отображения в админке. Например: <i>Новости</i>, <i>Блог</i>, <i>Фотоальбом</i> и т.д."
#     )
#     bRollPublish = models.BooleanField(
#         default=True, db_index=True,
#         verbose_name="Вкл./Выкл. ролл",
#         help_text="Публиковать ролл через URN (URL-слаг). Если опубликовано, то и ролл "
#                   "можно будет адресовать по URL </i>/block/roll/content</i> и все "
#                   "связанные с ним единицы контента (и производные роллы в будущем). "
#                   "Если не опубликовано, то будет вызываться ошибка 404 (при обращении по URL или вызова как родителя)"
#                   " или отключаться (в случае наследования)."
#     )
#     kRollTemplate = models.ForeignKey(
#         'TbTemplate', blank=True, null=True,
#         default=None, on_delete=models.DO_NOTHING,
#         related_name='kRollTemplate',     # из-за конфликта "магии" Джанго иначе не работает из-за парных ForeignKey
#         db_constraint=False,
#         verbose_name="Шаблон ролла",
#         help_text="Шаблон отвечающий за отображение списка      <br />контента для категории.<br />"
#                   "<b style='color:red'>ПОДУМАЙТЕ ПЕРЕД ТЕМ КАК ИЗМЕНЯТЬ!!</b>"
#     )
#     kDefaultContentTemplate = models.ForeignKey(
#         'TbTemplate', blank=True, null=True,
#         default=None, on_delete=models.DO_NOTHING,
#         related_name='kContentTemplate',  # из-за конфликта "магии" Джанго иначе не работает из-за парных ForeignKey
#         db_constraint=False,
#         verbose_name="Шаблон контента (по умолчанию)",
#         help_text="Шаблон (по умолчанию) который будет использован<br />"
#                   "для типовых единиц контента в этом ролле.<br />"
#                   "<b style='color:red'>ПОДУМАЙТЕ ПЕРЕД ТЕМ КАК ИЗМЕНЯТЬ!!</b></br>"
#                   "<small>Для любой единицы контента шаблон можно будет<br />"
#                   "переназначить (например, если вы делаете контент-страницы<br>"
#                   "с уникальным дизайном).</small>"
#     )
#     iRollItemInPage = models.PositiveSmallIntegerField(
#         default=None, blank=True, null=True,
#         verbose_name="На странице",
#         help_text="Сколько контентных единиц будет отображено в ленте на одной странице при пейджинации.<br />"
#                   "<small><b>Если оставить пустым (или указать&nbsp;0), то будет выводиться вся лента без пейджинации"
#                   " (значение по умолчанию)</b></small>"
#     )
#     szRollSortRule = models.CharField(
#         max_length=128, blank=True, null=True,
#         default="-dtCreate",
#         verbose_name="Правило сортировки",
#         help_text="Правило сортировки контента в ролле. Используются конструкции <b>order_by</b> для Django. "
#                   "Например: <tt><u>dtCreate</u></tt> или <nobr><tt><u>-dtCreate</u></tt></nobr>, или "
#                   "<tt><u>szTitle</u></tt>, или <nobr><tt><u>-szTitle</u></tt></nobr>  …",
#     )
#     szRollFilterRule = models.CharField(
#         max_length=128, blank=True, null=True,
#         default="bPublish=True",
#         verbose_name="Правило фильтрации",
#         help_text="Правило фильтрации контента в ролле. Используются конструкции <b>filter</b> для Django. "
#                   "Например: <nobr><tt><u>dtCreate__gte=2019-01-01</u></tt></nobr> или "
#                   "<nobr><tt><u>dtCreate__lte=2019-01-01</u></tt></nobr> …",
#     )
#     szRollTitle = models.CharField(
#         max_length=255, blank=True, null=True,
#         verbose_name="Заголовок ролла",
#         help_text="Заголовок ролла. Отображается в шаблоне ролла в теге <i>title</i>."
#                   "<br /><b style='color:red'>ТИПОГРАФИРУЕТСЯ!!</b> Может содержать HTML-теги.",
#     )
#     kRollImgPreview = FilerFileField(
#         null=True, blank=True, on_delete=models.SET_NULL,
#         related_name="preview",
#         verbose_name="Превью ролла",
#         help_text="Картинка-превью или любая заголовочная картинка. Например, для фон под заголовком, "
#                   "логотип брендирования и т.п.",
#     )
#     szRollText = models.TextField(
#         default="", null=True, blank=True,
#         verbose_name='Текст ролла (тизер)',
#         help_text="Текст ролла (пояснения перед новостной лентой, блогом и пр.)</br><small>(разрешен "
#                   "HTML-код, будет обработан типографом, если типограф включен)</small>"
#     )
#     szRollRedirectTo = models.CharField(
#         max_length=500, default="", blank=True, null=True,
#         verbose_name="Редирект на",
#         help_text="Иногда нужно, чтобы ролл (пункт меню) был редиректом на другой URL, например когда"
#                   "ролл снят с публикации (включен) и нужно перенаправить трафик.<br/>"
#                   "<small>допустимы как внутренние URL-ссылки от корня сайта '/………',"
#                   " так и внешние URI-ссылки 'http://………'</small>"
#     )
#     dtRollCreate = models.DateTimeField(
#         auto_now_add=True,  # надо указать False при миграции, после вернуть в True
#         # для выполнения миграций нужно добавлять default, а после она не нужна
#         # default=datetime.now(pytz.timezone(settings.TIME_ZONE)),
#         verbose_name="Дата Создания"
#     )
#     dtRollTimeStamp = models.DateTimeField(
#         auto_now=True,  # надо указать False при миграции, после вернуть в True
#         # для выполнения миграций нужно добавлять default, а после она не нужна
#         # default=datetime.now(pytz.timezone(settings.TIME_ZONE)),
#         verbose_name="Штамп времени"
#     )
#
#     def __unicode__(self):
#         return f"{self.id:03}: {self.szRollSlug}"
#
#     def __str__(self):
#         return self.__unicode__()
#
#     class Meta:
#         verbose_name = "[…Ролл (список)] ☷⇊"
#         verbose_name_plural = "[…Роллы (списки)] ☷⇊"
#         ordering = ['id', ]
