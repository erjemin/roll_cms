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
    # szRollUrlTo        | Url (например, редирект ролла)       | varchar(200) | YES  | ""      |                |
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
        verbose_name="<r>-Шаблон",
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
                  "<b style=\"color:red\">ПОДУМАЙТЕ ПЕРЕД ТЕМ КАК ИЗМЕНЯТЬ!!</b><br />"
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
        help_text="Текст ролла (пояснения перед новостной лентой, блогом и пр.)<br />"
                  "<small>разрешен HTML-код и может быть обработан типографом (если типограф включен)</small>"
    )
    szRollUrlTo = models.URLField(
        default="", blank=True, null=True,
        verbose_name="URL на",
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
        verbose_name = " <r> Ролл (лента)"
        verbose_name_plural = " <r> Роллы (ленты)"
        ordering = ["id", ]


class TbItem(models.Model):
    """ Элементы контента. Таблица в БД `roll_cms_tbitem` """
    # -------------------+--------------------------------------+--------------+------+---------+----------------+
    # Поле               | Назначение                           | Тип          | NULL | DEFAULT | Extra          |
    # -------------------+--------------------------------------+--------------+------+---------+----------------+
    # id                 | primary key (pk)                     | bigint(20)   | NOT  |         | auto_increment |
    # kRoll_id           | Ролл (лента) в которую вкл. элемент  | bigint(20)   | ---  | NULL    | foreign key    |
    # bPublish           | Вкл./Выкл. элемент (опубликован)     | tinyint(1)   | NOT  | 1       | index          |
    # tdStart            | Дата публикации элемента             | datetime(6)  | NOT  | NOW()   | index          |
    # tdStop             | Дата снятия элемента                 | datetime(6)  | YES  | NULL    | index          |
    # iSort              | Сортировка элемента в ролле          | smallint     | YES  | 0       | index          |
    # iCount             | Счётчик просмотров элемента          | bigint(20)   | YES  | 0       | index          |
    # szTitle            | Заголовок элемента                   | varchar(768) | YES  | ""      |                |
    # kImg_id            | Картинка-превью элемента             | int(11)      | YES  | NULL    | foreign key    |
    # szNote             | Анонс элемента                       | text         | YES  | ""      |                |
    # szText             | Текст элемента                       | text         | YES  | ""      |                |
    # szSeoKeywords      | Keywords (SEO)                       | varchar(120) | YES  | ""      |                |
    # szSeoDescription   | Description (SEO)                    | varchar(160) | YES  | ""      |                |
    # szSlug             | URL-слаг элемента                    | varchar(155) | YES  | ""      | unique         |
    # jOldSlugs          | Старые URL-слаги элемента            | json         | YES  | NULL    |                |
    # szUrlTo            | URL на внешний ресурс                | varchar(200) | YES  | ""      |                |
    # jAtt               | Аттрибуты и таги (вложения) элемента | json         | YES  | NULL    |                |
    # kTemplate_id       | Шаблон (спец-шаблон) элемента        | bigint(20)   | YES  | NULL    | foreign key    |
    # dtCreate           | Дата создания элемента               | datetime(6)  | NOT  | NOW()   | index          |
    # dtTimeStamp        | Штамп времени (дата изменения)       | datetime(6)  | NOT  | NOW()   | index          |
    # -------------------+--------------------------------------+--------------+------+---------+----------------+
    kRoll = models.ManyToManyField(
        to="roll_cms.TbRoll",
        default=None, blank=True,       # null=True,    # null -- не имеет смысла для ManyToManyField
        related_name="in_roll",
        # through="roll_cms.TbItem2Roll", # возможно стоит сделать через промежуточную спец-таблицу с сортером (меню)
        verbose_name=u"Ролл",
        help_text="Ролл (лента) в которую включен элемент. Может быть несколько роллов, в которые включен элемент."
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
    iCount = models.PositiveBigIntegerField(
        default=0, db_index=True,
        verbose_name="Счётчик",
        help_text="Целое число.<br /><small>Может использоваться для подсчёта<br/>количества просмотров элемента.</small>"
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
        help_text="Анонс/Тизер/Заметка<br />"
                  "<small>разрешен HTML-код и может быть обработан типографом (если типограф включен)</small>"
    )
    szText = models.TextField(
        default="", null=True, blank=True,
        verbose_name="Текст",
        help_text="Текст/Контент/Запись<br />"
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
    szUrlTo = models.URLField(
        default="", blank=True, null=True,
        verbose_name="URL на",
        help_text="URL-ссылка на внешний ресурс (например для создания рекламных баннеров).<br />"
                  "<small>допустимы как внутренние URL-ссылки от корня сайта \"/……/……\","
                  " так и внешние URI-ссылки \"http://……/……\"</small>"
    )
    kRollTo = models.ForeignKey(
        to="roll_cms.TbRoll", blank=True, null=True,
        default=None, on_delete=models.DO_NOTHING,
        db_constraint=False,
        related_name="roll_to",
        verbose_name="Вложенный ролл",
        help_text="Вложенный ролл (лента) на который, например будет редирект при обращении к этому элементу.<br />"
                  "<small>Если указан, то при обращении к этому элементу будет произведен редирект на указанный ролл."
                  " Вложенный ролл, сработает как URL-ссылка, но в отличии от URL-ссылки, при изменении слага у ролла"
                  " ничего не сломается&hellip; Впрочем, поведение задается в шаблоне элемента.</small>"
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


class TbMenu(models.Model):
    """ Меню. Таблица в БД `roll_cms_tbmenu` """
    # -------------------+--------------------------------------+--------------+------+---------+----------------+
    # Поле               | Назначение                           | Тип          | NULL | DEFAULT | Extra          |
    # -------------------+--------------------------------------+--------------+------+---------+----------------+
    # id                 | primary key (pk)                     | bigint(20)   | NOT  |         | auto_increment |
    # szMenuName         | Название меню                        | varchar(32)  | NOT  |         | unique         |
    # kMenuTemplateFrom  | Шаблон-Источник                      | bigint(20)   | YES  | NULL    | foreign key    |
    # kMenuTemplateTo    | Кэш-Шаблон                           | bigint(20)   | YES  | NULL    | foreign key    |
    # dtMenuCreate       | Дата создания меню                   | datetime(6)  | NOT  | NOW()   | index          |
    # dtMenuTimeStamp    | Штамп времени (дата изменения меню)  | datetime(6)  | NOT  | NOW()   | index          |
    # -------------------+--------------------------------------+--------------+------+---------+----------------+
    szMenuName = models.CharField(
        max_length=32, blank=False, null=False, db_index=True, unique=True,
        verbose_name="Название",
        help_text="Техническое название меню (для админки)"
    )
    kMenuTemplateFrom = models.ForeignKey(
        to="roll_cms.TbTemplate", blank=True, null=True,
        default=None, on_delete=models.DO_NOTHING,
        related_name="kMenuTemplate_From",  # из-за конфликта "магии" Джанго иначе не работает из-за парных ForeignKey
        db_constraint=False,
        verbose_name="Шаблон-Источник",
        help_text="Шаблон отвечающий за отображение меню.<br />"
                  "<b style=\"color:red\">ПОДУМАЙТЕ ПЕРЕД ТЕМ КАК ИЗМЕНЯТЬ!!</b>"
    )
    kMenuTemplateTo = models.ForeignKey(
        to="roll_cms.TbTemplate", blank=True, null=True,
        default=None, on_delete=models.DO_NOTHING,
        db_constraint=False,
        related_name="kMenuTemplate_Cash",  # из-за конфликта "магии" Джанго иначе не работает из-за парных ForeignKey
        verbose_name="Кэш-Шаблон",
        help_text="Шаблон, который станет кешем (обновляется из шаблона-источника).<br />"
                  "Если оставить пустым, то кеширование не будет производиться.<br />"
                  "<b style=\"color:red\">ПОДУМАЙТЕ ПЕРЕД ТЕМ КАК ИЗМЕНЯТЬ!!</b>"
    )
    dtMenuCreate = models.DateTimeField(
        auto_now_add=True,  # надо указать False при миграции, после вернуть в True
        # для выполнения миграций нужно добавлять default, а после она не нужна
        # default=datetime.now(pytz.timezone(settings.TIME_ZONE)),
        db_index=True,
        verbose_name="Дата Создания"
    )
    dtMenuTimeStamp = models.DateTimeField(
        auto_now=True,  # надо указать False при миграции, после вернуть в True
        # для выполнения миграций нужно добавлять default, а после она не нужна
        # default=datetime.now(pytz.timezone(settings.TIME_ZONE)),
        db_index=True,
        verbose_name="Штамп времени"
    )

    def __unicode__(self):
        return f" ({self.id:02x}) {self.szMenuName}"

    def __str__(self):
        return self.__unicode__()

    class Meta:
        verbose_name = " [m] Меню"
        verbose_name_plural = " [m] Меню"
        ordering = ["id", ]


class TbMenuPoint(models.Model):
    """ Пункты меню. Таблица в БД `roll_cms_tbmenupoint` """
    # -------------------+--------------------------------------+--------------+------+---------+----------------+
    # Поле               | Назначение                           | Тип          | NULL | DEFAULT | Extra          |
    # -------------------+--------------------------------------+--------------+------+---------+----------------+
    # id                 | primary key (pk)                     | bigint(20)   | NOT  |         | auto_increment |
    # kMenu_id           | Меню к которому принадлежит пункт    | bigint(20)   | NOT  | NULL    | foreign key    |
    # bbPointPublish     | Опубликован пункт меню               | tinyint(1)   | NOT  | 1       | index          |
    # szPointName        | Название пункта меню (техническое)   | varchar(32)  | NOT  | ""      |                |
    # szPointTitle       | Поинт-Тайтл (html)                   | text         | YES  | ""      |                |
    # iPontSort          | Сортировка пункта в меню             | smallint     | YES  | 0       | index          |
    # kPoint2Roll_id     | Ролл на который переходит пункт      | bigint(20)   | YES  | NULL    | foreign key    |
    # kPoint2Item_id     | Элемент на который переходит пункт   | bigint(20)   | YES  | NULL    | foreign key    |
    # kPoint2Menu_id     | Подменю                              | bigint(20)   | YES  | NULL    | foreign key    |
    # szPointUtlTo       | URL                                  | varchar(200) | YES  | ""      |                |
    # tdPointCreate      | Дата создания пункта                 | datetime(6)  | NOT  | NOW()   | index          |
    # tdPointTimeStamp   | Штамп времени (дата изменения пункта)| datetime(6)  | NOT  | NOW()   | index          |
    # -------------------+--------------------------------------+--------------+------+---------+----------------+
    kMenu = models.ForeignKey(
        to="roll_cms.TbMenu", blank=False, null=False, default=None,
        on_delete=models.DO_NOTHING,
        related_name="kMenu",
        verbose_name="Меню",
        help_text="Меню, к которому принадлежит этот пункт"
    )
    bPointPublish = models.BooleanField(
        default=True, db_index=True,
        verbose_name="Опуб…",
        help_text="Опубликованный пункт будет отображаться в меню.<br /><small>Поведение не опубликованного пункта"
                  " зависит от шаблона меню.<br />Например, пункт может быть «погашен» в меню с помощью<br />disabled"
                  " или display:none, или другим способом.</small>"
    )
    szPointName = models.CharField(
        max_length=32, blank=False, null=False, default="",
        verbose_name="Название",
        help_text="Техническое название пункта меню (для админки)",
    )
    szPointTitle = models.TextField(
        blank=True, null=True, default="",
        verbose_name="Поинт-Тайтл",
        help_text="Заголовок пункта меню (то, как пункт отображается в шаблоне). Допустим html и даже сложный код,"
                  " так как пункт меню может быть текстом, иконкой, картинкой, csv и т.п.)"
    )
    iPontSort = models.SmallIntegerField(
        default=0, db_index=True,
        verbose_name="Сорт.",
        help_text="Целое число.<br /><small>Для сортировки пунктов, при отображении меню. Чем меньше число, тем"
                  " выше(раньше) пункт в меню</small>"
    )
    kPoint2Roll = models.ForeignKey(
        to='roll_cms.TbRoll', blank=True, null=True,
        on_delete=models.DO_NOTHING,
        related_name="menu2roll",
        verbose_name="Ролл",
        help_text="Ролл, на который будет переход при клике по этому пункту меню<br />"
                  "<small><b style=\"color:red\">Ролл при формировании меню имеет наивысший приоритет и отображается"
                  "<br />вместо других!</b> Если нужен редирект, то используйте поле «URL на» внутри ролла.</small>")
    kPoint2Item = models.ForeignKey(
        to='roll_cms.TbItem', blank=True, null=True,
        on_delete=models.DO_NOTHING,
        related_name="menu2item",
        verbose_name="Элемент",
        help_text="Элемент, на который будет переход при клике по этому пункту меню<br /> "
                  "<small><b style=\"color:red\">Элемент при формировании меню имеет второй приоритет и отображается"
                  "<br />только если нет ролла!</b> Если нужен редирект, то используйте поле «URL на» элемента.</small>"
    )
    kPoint2Menu = models.ForeignKey(
        to='roll_cms.TbMenu', blank=True, null=True,
        on_delete=models.DO_NOTHING,
        related_name="menu2menu",
        verbose_name="Подменю",
        help_text="Подменю, будет отображаться при наведении на этот пункт меню<br />"
                  "<small><b style=\"color:red\">Подменю при формировании меню имеет самый низший приоритет<br />"
                  "и отображается только если нет ролла и элемента!</b></small>"
    )
    szPointUtlTo = models.CharField(
        default="", blank=True, null=True, max_length=200,
        verbose_name="URL на",
        help_text="URL-ссылка на внешний/внутренний ресурс (например для «Дом») для ленивых.<br />"
                  "<small><b style=\"color:red\">Если URL установлен, то он отменит все остальные переходы (роллы,\
                   элементы и меню)!</b><br />допустимы как внутренние URL-ссылки от корня сайта \"/……/……\","
                  " так и внешние URI-ссылки \"http://……/……\"</small>"
    )
    tdPointCreate = models.DateTimeField(
        auto_now_add=True,  # надо указать False при миграции, после вернуть в True
        # для выполнения миграций нужно добавлять default, а после она не нужна
        # default=datetime.now(pytz.timezone(settings.TIME_ZONE)),
        db_index=True,
        verbose_name="Дата Создания"
    )
    tdPointTimeStamp = models.DateTimeField(
        auto_now=True,  # надо указать False при миграции, после вернуть в True
        # для выполнения миграций нужно добавлять default, а после она не нужна
        # default=datetime.now(pytz.timezone(settings.TIME_ZONE)),
        db_index=True,
        verbose_name="Штамп времени"
    )

    def __unicode__(self):
        return f" ({self.id:02x}) {self.szPointName}"

    def __str__(self):
        return self.__unicode__()

    class Meta:
        verbose_name = " [p] Пункт меню"
        verbose_name_plural = " [p] Пункты меню"
        ordering = ["iPontSort", "tdPointCreate", ]

