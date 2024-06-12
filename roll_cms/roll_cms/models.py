# -*- coding: utf-8 -*-
import random

from django.db import models
from django.utils.timezone import now
from filer.fields.image import FilerImageField
# from ckeditor.fields import RichTextField
# from ckeditor_uploader.fields import RichTextUploadingField
from datetime import datetime
from roll_cms.add_function import safe_html_special_symbols
from roll_cms.settings import *
from roll_cms.add_function import log_p
import os
import re
import pytils
# import datetime
# import urllib3
import json


class TbTemplate(models.Model):
    """ Шаблоны. Таблица в БД `roll_cms_tbtemplate` """
    # --------------+----------------------------------+--------------+------+---------+----------------+
    # Поле          | Назначение                       | Тип          | NULL | DEFAULT | Extra          |
    # --------------+----------------------------------+--------------+------+---------+----------------+
    # id            | первичный ключ                   | bigint(20)   | NO   | NULL    | auto_increment |
    # szFileName    | имя файла шаблона                | varchar(100) | YES  | ""      | unique         |
    # szJinjaCode   | код шаблона                      | longtext     | YES  | ""      |                |
    # szDescription | назначение/описание шаблона      | varchar(100) | YES  | ""      |                |
    # szVar         | переменная для передачи значений | varchar(16)  | YES  | "var"   |                |
    # --------------+----------------------------------+--------------+------+---------+----------------+
    szFileName = models.CharField(
        # primary_key=True,  # первичный ключ
        default=".jinja2", db_index=True, unique=True,  # индекс и уникальность
        null=True, blank=True,
        max_length=100,
        verbose_name="FILENAME Шаблона",
        help_text="Имя файла шаблона (расширение <b>.jinja2</b> / <b>.j2</b> / <b>.jinja</b> (для шаблонов Jinja2) или "
                  "<b>.html</b> / <b>.htm</b> (для шаблонов Django).<br/>"
                  "Все остальные расширения считаются шаблонами Django и будет добавлено расширение <b>html</b>.<br/>"
                  "<small style=\"color:red\">ПОДУМАЙТЕ ПЕРЕД ТЕМ КАК ИЗМЕНЯТЬ ИМЯ ФАЙЛА ШАБЛОНА!!</small>",
    )
    szJinjaCode = models.TextField(
        default="", null=True, blank=True,
        verbose_name="Код шаблона",
        help_text="Код шаблона (jinja2 или django).<br/>"
                  "<small>Если оставить поле пустым при создании шаблона, то при его сохранении будет проверено"
                  "наличие шаблона с таким FILENAME и, если он существует, то его содержимое будет записано"
                  "в это поле.</small>",

    )
    szDescription = models.CharField(
        max_length=100,
        default="", null=True, blank=True,
        verbose_name="Описание",
        help_text="Назначение/описание шаблона",
    )
    szVar = models.CharField(
        max_length=16, default="var",
        null=True, blank=True,
        verbose_name="Переменная",
        help_text="Переменная через которую этот шаблон принимает данные",
    )

    def __unicode__(self):
        return f"{self.szFileName}"

    def __str__(self):
        return self.__unicode__()

    # переопределяем save() для записи шаблонов не только в ДБ, но и в файл
    def save(self, *args, **kwargs):
        # path_filename = TEMPLATES_DIR / self.szFileName
        if self.szFileName.lower().endswith((".jinja2", ".j2", ".jinja", )):
            # нужно будет создавать шаблон для шаблонизатора Jinja2
            path_filename = TEMPLATES[0]["DIRS"][0] / self.szFileName
        elif self.szFileName.lower().endswith((".htm", ".html", )):
            # нужно будет создавать шаблон для шаблонизатора Django
            path_filename = TEMPLATES[1]["DIRS"][0] / self.szFileName
        else:
            # неизвестный формат шаблона
            path_filename = TEMPLATES[1]["DIRS"][0] / f"{self.szFileName}.html"
        if not self.pk and re.sub(r"\s", "", self.szJinjaCode) == "":
            # Это не редактирование, а создание нового шаблона.
            # Нужно проверить, вдруг файл шаблона с таким именем уже существует?
            # Но если проверка покажет, что файл с таким именем существует, то надо будет в любом случае прочитать его
            # и записать в поле szJinjaCode, а после занести в базу!!! Ну и зачем проверить тогда!! Сразу читаем, и
            # если вывалится по ошибке -- то шаблона нет (или не хватает прав для его чтения).
            try:
                with open(path_filename, "r", encoding="utf-8") as template:
                    self.szJinjaCode = template.read()
                    super(TbTemplate, self).save(*args, **kwargs)
                    return
            except FileNotFoundError:
                # это действительно новый шаблон, но с пустым содержанием
                pass
        # проверим, если нет каталога в котором нужно сохранить шаблон, то создадим его
        if not os.path.exists(os.path.dirname(path_filename)):
            # TODO: проверка на существование каталога у шаблона не работает если каталог имеет большую вложенность >=2
            os.makedirs(os.path.dirname(path_filename))
        with open(path_filename, "w+", encoding="utf-8") as tmplt_file:
            tmplt_file.write(self.szJinjaCode.replace("\r\n", "\n"))
        # для продакшн (not DEBUG) нужно "дёрнуть" файл-touch_reload, чтобы uWSGI "щёлкнул"
        # (или отключить кеширование шаблонов в Django, что замедлит работу сайта)
        with open(TOUCH_RELOAD, "a") as f:
            f.write(log_p(msg=f"TEMPLATE \"{self.szFileName}\" RELOAD", status="OK")+"\n")
        super(TbTemplate, self).save(*args, **kwargs)

    # переопределяем метод delete() (пока, не удаляется)
    def delete(self, *args, **kwargs):
        pass
        # TODO: может быть добавить переименование файлов шаблона и удаление записи его из базы...
        # super(TbTemplate, self).delete(*args, **kwargs)

    class Meta:
        verbose_name = " {T} …Шаблон"
        verbose_name_plural = " {T} …Шаблоны"


class TbRoll(models.Model):
    """ Роллы. Они объединяют однородные по представлению сущности (ленты новостей, блоги, фотоальбомы,
    баннеры, товары и т.д.). Таблица в БД `roll_cms_tbroll` """
    # -------------------+--------------------------------------+--------------+------+---------+----------------+
    # Поле               | Назначение                           | Тип          | NULL | DEFAULT | Extra          |
    # -------------------+--------------------------------------+--------------+------+---------+----------------+
    # id                 | primary key (pk)                     | bigint(20)   | NOT  |         | auto_increment |
    # szRollSlug         | URL-слаг                             | varchar(155) | YES  | ""      | unique         |
    # jRollOldSlugs      | Старые URL-слаги                     | json         | YES  | NULL    |                |
    # szRollName         | Имя ролла  (техническое)             | varchar(64)  | NOT  |         | unique         |
    # bRollPublished     | Вкл./Выкл. ролл (опубликован)        | tinyint(1)   | NOT  | 1       | index          |
    # kRollTemplate_id   | Шаблон ролла                         | bigint(20)   | YES  | NULL    | foreign key(?) |
    # kDefaultContentTemplate_id | Шаблон контента (default)    | bigint(20)   | YES  | NULL    | foreign key(?) |
    # iRollItemInPage    | Число единиц контента при паджинации | smallint unsigned | YES | 10  | >= 0           |
    # szRollSortRule     | Правило сортировки по умолчанию      | varchar(64)  | YES  | "-dtCreate"     |        |
    # szRollFilterRule   | Правило фильтрации по умолчанию      | varchar(64)  | YES  | "bPublish=True" |        |
    # szRollTitle        | Заголовок ролла                      | varchar(255) | YES  | ""      | index          |
    # kRollImgPreview_id | Картинка-превью ролла                | int(11)      | YES  | NULL    | foreign key    |
    # szRollText         | Тизер-текст ролла                    | text         | YES  | ""      |                |
    # szRollRedirectTo   | Перенаправление ролла                | varchar(500) | YES  | ""      |                |
    # dtRollCreate       | Дата создания ролла                  | datetime(6)  | NOT  | NOW()   | index          |
    # dtRollTimeStamp    | Штамп времени (дата изменения ролла) | datetime(6)  | NOT  | NOW()   | index          |
    # -------------------+--------------------------------------+--------------+------+---------+----------------+
    szRollSlug = models.SlugField(
        default="", max_length=SLUG_LENGTH, blank=True, null=True, db_index=True, unique=True,
        verbose_name="URL-слаг",
        help_text=f"URL-слаг страницы… {SLUG_LENGTH} символа (пробелы заменяются \"-\").<br/>"
                  f"<small><b>Если оставить пустым, то URL-слаг сформируется автоматически</b></small>"
    )
    jRollOldSlugs = models.JSONField(
        default=list, blank=True, null=True,
        verbose_name="Старые URL-слаги",
        help_text="JSON-список строк (типа <b>[\"старый_слаг_1\", \"старый_слаг_2\", \"и так далее\", ]</b>) из"
                  " предыдущих URL-слагов, которые использовались для этого ролла ранее. Возможно нужно для корректной"
                  " переиндексации страниц поисковиками при изменении слага на давно работающем публичном сайте.<br/>"
                  "<small>Используется для редиректа с предыдущих URL-слагов на текущий. Попытка найти возможный"
                  " редирект будет производиться только при обработке ошибки 404 (страница не найдена) и поэтому"
                  " может быть <b>перекрыт</b> существующим слагом другого ролла. Кроме того, следует учесть, что "
                  " редиркеты по старым слагам, в силу отсутствия сквозных индексов, будет очень медленным и порождать"
                  " лишнюю нагрузку... Редирект будет производится с кодом 301 (постоянный редирект)</small><br />"
                  "<b style=\"color:red\">Список создается автоматически, но доступен для редактирования"
                  " (например, для удаления слагов, редиректы для которых больше не требуется)</b>"
    )
    szRollName = models.CharField(
        max_length=64, blank=False, null=False,
        verbose_name="Имя ролла (техническое)",
        help_text="Техническое название ролла (наименование категории, раздела, сборника)<br/>"
                  "для отображения в админке. Например: <i>Новости</i>, <i>Блог</i>, <i>Фотоальбом</i> и т.д."
    )
    bRollPublish = models.BooleanField(
        default=True, db_index=True,
        verbose_name="Опуб...",
        help_text="Публиковать ролл через URN (URL-слаг). Если опубликовано, то и ролл "
                  "можно будет адресовать по URL </i>/block/roll/content</i> и все "
                  "связанные с ним единицы контента (и производные роллы в будущем). "
                  "Если не опубликовано, то будет вызываться ошибка 404 (при обращении по URL или вызова как родителя)"
                  " или отключаться (в случае наследования)."
    )
    kRollTemplate = models.ForeignKey(
        to="roll_cms.TbTemplate", blank=True, null=True,
        default=None, on_delete=models.DO_NOTHING,
        related_name="kRollTemplate",     # из-за конфликта "магии" Джанго иначе не работает из-за парных ForeignKey
        db_constraint=False,
        verbose_name="[r]-Шаблон",
        help_text="Шаблон отвечающий за отображение списка<br />контента для категории.<br />"
                  "<b style=\"color:red\">ПОДУМАЙТЕ ПЕРЕД ТЕМ КАК ИЗМЕНЯТЬ!!</b>"
    )
    kDefaultContentTemplate = models.ForeignKey(
        to="roll_cms.TbTemplate", blank=True, null=True,
        default=None, on_delete=models.DO_NOTHING,
        related_name="kContentTemplate",  # из-за конфликта "магии" Джанго иначе не работает из-за парных ForeignKey
        db_constraint=False,
        verbose_name="<i>-Шаблон",
        help_text="Шаблон (по умолчанию для элементов) который будет использован<br />"
                  "для типовых элементов контента в этом ролле.<br />"
                  "<b style=\"color:red\">ПОДУМАЙТЕ ПЕРЕД ТЕМ КАК ИЗМЕНЯТЬ!!</b></br>"
                  "<small>Для любой единицы контента шаблон можно будет<br />"
                  "переназначить (например, если вы делаете контент-страницы<br>"
                  "с уникальным дизайном).</small>"
    )
    iRollItemInPage = models.PositiveSmallIntegerField(
        default=10, blank=True, null=True,
        verbose_name="На странице",
        help_text="Сколько контентных единиц будет отображено в ленте на одной странице при пейджинации.<br />"
                  "<small><b>Если оставить пустым (или указать&nbsp;0), то будет выводиться вся лента без пейджинации"
                  " (значение по умолчанию)</b></small>"
    )
    szRollSortRule = models.CharField(
        max_length=128, blank=True, null=True,
        default="-dtCreate",
        verbose_name="Правило сортировки",
        help_text="Правило сортировки контента в ролле. Используются конструкции <b>order_by</b> для Django. "
                  "Например: <tt><u>dtCreate</u></tt> или <nobr><tt><u>-dtCreate</u></tt></nobr>, или "
                  "<tt><u>szTitle</u></tt>, или <nobr><tt><u>-szTitle</u></tt></nobr> …",
    )
    szRollFilterRule = models.CharField(
        max_length=128, blank=True, null=True,
        default="bPublish=True",
        verbose_name="Правило фильтрации",
        help_text="Правило фильтрации контента в ролле. Используются конструкции <b>filter</b> для Django. "
                  "Например: <nobr><tt><u>dtCreate__gte=2019-01-01</u></tt></nobr> или "
                  "<nobr><tt><u>dtCreate__lte=2019-01-01</u></tt></nobr> …",
    )
    szRollTitle = models.CharField(
        max_length=255, blank=True, null=True, db_index=True,
        verbose_name="Заголовок ролла",
        help_text="Заголовок ролла. Отображается в шаблоне ролла в теге <i>title</i>.<br />"
                  "<b style=\"color:red\">ТИПОГРАФИРУЕТСЯ!!</b> <small>Может содержать HTML-теги (кроме блоковых"
                  " тегов &lt;div&gt;, &lt;p&gt;, &lt;ul&gt; и подобных) и мнемокод (например &amp;laquo;,"
                  " &amp;raquo;, &amp;shy; и т.п.).</small>",
    )
    kRollImgPreview = FilerImageField(
        null=True, blank=True, on_delete=models.SET_NULL,
        # related_name="roll-preview",
        verbose_name="Превью ролла",
        help_text="Картинка-превью или любая заголовочная картинка. Например, для фон под заголовком, "
                  "логотип брендирования и т.п.",
    )
    szRollText = models.TextField(
        default="", null=True, blank=True,
        verbose_name="Текст ролла (тизер)",
        help_text="Текст ролла (пояснения перед новостной лентой, блогом и пр.)</br>"
                  "<small>разрешен HTML-код и может быть обработан типографом (если типограф включен)</small>"
    )
    szRollRedirectTo = models.CharField(
        max_length=500, default="", blank=True, null=True,
        verbose_name="Редирект на",
        help_text="Иногда нужно, чтобы ролл (пункт меню) был редиректом на другой URL, например когда"
                  "ролл снят с публикации (выключен) и нужно перенаправить трафик.<br/>"
                  "<small>допустимы как внутренние URL-ссылки от корня сайта \"/……/……\","
                  " так и внешние URI-ссылки \"http://……/……\"</small>"
    )
    dtRollCreate = models.DateTimeField(
        auto_now_add=True,  # надо указать False при миграции, после вернуть в True
        # для выполнения миграций нужно добавлять default, а после она не нужна
        # default=datetime.now(pytz.timezone(settings.TIME_ZONE)),
        db_index=True,
        verbose_name="Дата Создания"
    )
    dtRollTimeStamp = models.DateTimeField(
        auto_now=True,  # надо указать False при миграции, после вернуть в True
        # для выполнения миграций нужно добавлять default, а после она не нужна
        # default=datetime.now(pytz.timezone(settings.TIME_ZONE)),
        db_index=True,
        verbose_name="Штамп времени"
    )

    def __unicode__(self):
        return f"{self.id:03}: {self.szRollSlug}"

    def __str__(self):
        return self.__unicode__()

    class Meta:
        verbose_name = " [r] Ролл (лента)"
        verbose_name_plural = " [r] Роллы (ленты)"
        ordering = ["id", ]


class TbItem(models.Model):
    # ============================================================
    # ТАБЛИЦА TbItem (единицы, элемент контента): новости, записи в блоке, элементы списков и лент,
    # баннеры и всё что угодно...
    # ============================================================
    kRoll = models.ManyToManyField(
        to="roll_cms.TbRoll",
        default=None, blank=True,       # null=True,    # null -- не имеет смысла для ManyToManyField
        # through="roll_cms.TbItem2Roll", # возможно стоит сделать через промежуточную спец-таблицу с сортером (меню)
        verbose_name=u"Ролл"
    )
    bPublish = models.BooleanField(
        default=True, db_index=True,
        verbose_name="Опуб…",
        help_text="Опубликовано. Элемент будет отображаться в соответствующей ленте категории и"
                  "&nbsp;при его просмотре будет отображаться навигация «Предыдущий/Следующий»."
    )
    tdStart = models.DateTimeField(
        db_index=True,  default=now,   # datetime.date.today(),
        verbose_name="Дата публикации",
        help_text=u"C этого момента элемент<br/>появится на сайте."
    )
    tdStop = models.DateTimeField(
        db_index=True,  default=None, blank=True, null=True,
        verbose_name="Дата снятия",
        help_text=u"После этой даты элемент<br/>не отображается на сайте."
    )
    iSort = models.SmallIntegerField(
        default=0, db_index=True,
        verbose_name="Сорт.",
        help_text="Целое число.<br /><small>Может использоваться для сортировки<br/>элементов в ролле. Зависит от<br/>"
                  "настроек правил фильтрации в ролле.</small>"
    )
    szTitle = models.CharField(
        max_length=768, default="", blank=False, null=False,
        verbose_name="Заголовок",
        help_text="Заголовок <br />"
                  "<b style=\"color:red\">ТИПОГРАФИРУЕТСЯ!!</b> <small>Может содержать HTML-теги (кроме блоковых"
                  " тегов &lt;div&gt;, &lt;p&gt;, &lt;ul&gt; и подобных) и мнемокод (например &amp;laquo;,"
                  " &amp;raquo;, &amp;shy; и т.п.). Максимальная длинна <b>512 символов</b>)</small>"
    )
    kImg = FilerImageField(
        null=True, blank=True, on_delete=models.SET_NULL,
        # related_name="preview",
        verbose_name="IMG",
        help_text="Любая картинка, csv или файл. Может использоваться как превью к элементу, баннер, иконка"
                  " объект фотогалереи, списка документов и т.п."
    )
    szNote = models.TextField(
        default="", null=True, blank=True,
        verbose_name="Анонс",
        help_text="Анонс/Тизер/Заметка</br>"
                  "<small>разрешен HTML-код и может быть обработан типографом (если типограф включен)</small>"
    )
    szText = models.TextField(
        default="", null=True, blank=True,
        verbose_name="Текст",
        help_text="Текст/Контент/Запись</br>"
                  "<small>разрешен HTML-код и может быть обработан типографом (если типограф включен)</small>"
    )
    szSeoKeywords = models.CharField(
        default="", max_length=120, blank=True, null=True,
        verbose_name="Keywords (SEO)",
        help_text="Ключевые слова для поисковой оптимизации. Через запятую. 120 символов (поисковики больше все"
                  " равно «не проглотят»)."
    )
    szSeoDescription = models.CharField(
        default="", max_length=160, blank=True, null=True,
        verbose_name="Description (SEO)",
        help_text="Описание страницы для поисковой оптимизации. 160 символов (поисковики больше все"
                  " равно «не проглотят»).<br /><small><b>Если оставить пустым, то описание сформируется автоматически"
                  " на базе заголовка анонса</b></small>"
    )
    szSlug = models.SlugField(
        default="", max_length=SLUG_LENGTH, blank=True, null=True, db_index=True, unique=True,
        verbose_name="URL-слаг",
        help_text=f"URL-слаг страницы… {SLUG_LENGTH} символов (пробелы заменяются \"-\").<br/>"
                  f"<small><b>Если оставить пустым, то URL-слаг сформируется автоматически</b></small>"
    )
    jOldSlugs = models.JSONField(
        default=list, blank=True, null=True,
        verbose_name="Старые URL-слаги",
        help_text="JSON-список строк (типа <b>[\"старый_слаг_1\", \"старый_слаг_2\", \"и так далее\", ]</b>) из"
                  " предыдущих URL-слагов, которые использовались для этого элемента. Возможно нужно для корректной"
                  " переиндексации страниц поисковиками при изменении слага на давно работающем публичном сайте.<br/>"
                  "<small>Используется для редиректа с предыдущих URL-слагов на текущий. Попытка найти возможный"
                  " редирект будет производиться только при обработке ошибки 404 (страница не найдена) и поэтому"
                  " может быть <b>перекрыт</b> существующим слагом другого ролла. Кроме того, следует учесть, что "
                  " редиркеты по старым слагам, в силу отсутствия сквозных индексов, будет очень медленным и порождать"
                  " лишнюю нагрузку... Редирект будет производится с кодом 301 (постоянный редирект)</small><br />"
                  "<b style=\"color:red\">Список создается автоматически, но доступен для редактирования"
                  " (например, для удаления слагов, редиректы для которых больше не требуется)</b>"
    )
    jAtt = models.JSONField(
        default=dict, blank=True, null=True,
        verbose_name="Атрибуты и теги",
        help_text="JSON-словарь (ключ-значение), который будет обработан логикой приложения и отображён через"
                  " соответствующий ключу шаблон (функционал пока не реализован). Например:<br />"
                  "<nobr><tt>{\"tags\":[\"новость\", \"событие\", \"акция\"],"
                  " \"author\":\"Иванов И.И.\", \"source\":\"url-источника\"}</tt></nobr> И так далее…"
    )
    kTemplate = models.ForeignKey(
        to="roll_cms.TbTemplate", blank=True, null=True,
        default=None, on_delete=models.DO_NOTHING,
        db_constraint=False,
        verbose_name="<i>-Шаблон",
        help_text="Для элементов с не типовым (уникальным) дизайном, можно назначить свой шаблон.<br />"
                  "<b style=\"color:red\">ПОДУМАЙТЕ ПЕРЕД ТЕМ КАК ИЗМЕНЯТЬ!!</b>"
    )
    dtCreate = models.DateTimeField(
        auto_now_add=True,     # надо указать False при миграции, после вернуть в True
        # для выполнения миграций нужно добавлять default, а после она не нужна
        # default=datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)),
        verbose_name="Дата Создания"
    )
    dtTimeStamp = models.DateTimeField(
        auto_now=True,           # надо указать False при миграции, после вернуть в True
        # для выполнения миграций нужно добавлять default, а после она не нужна
        # default=datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)),
        verbose_name="Штамп времени"
    )

    def __unicode__(self):
        return f"{self.id:03}: {self.szSlug}"

    def __str__(self):
        return self.__unicode__()

    class Meta:
        verbose_name = " <i> Элемент контента"
        verbose_name_plural = " <i> Элементы контента"
        ordering = ["iSort", "-tdStart", ]

