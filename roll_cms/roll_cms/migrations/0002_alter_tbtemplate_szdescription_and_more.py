# Generated by Django 4.2.2 on 2023-07-15 21:11

from django.db import migrations, models
import django.db.models.deletion
import filer.fields.file


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0015_alter_file_owner_alter_file_polymorphic_ctype_and_more'),
        ('roll_cms', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tbtemplate',
            name='szDescription',
            field=models.CharField(blank=True, default='', help_text='Назначение/описание шаблона', max_length=100, null=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='tbtemplate',
            name='szVar',
            field=models.CharField(blank=True, default='var', help_text='Переменная через которую этот шаблон принимает данные', max_length=16, null=True, verbose_name='Переменная'),
        ),
        migrations.CreateModel(
            name='TbRoll',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('szRollSlug', models.SlugField(blank=True, default='', help_text="URL-слаг страницы… 155 символа (пробелы заменяются '-').<br/><small><b>Если оставить пустым, то URL-слаг сформируется автоматически</b></small>", max_length=155, null=True, unique=True, verbose_name='URL-слаг')),
                ('szRollName', models.CharField(help_text='Техническое название ролла (наименование категории, раздела, сборника)<br/>для отобращения в админке. Например: <i>Новости</i>, <i>Блог</i>, <i>Фотоальбом</i> и т.д.', max_length=64, verbose_name='Имя')),
                ('bRollPublish', models.BooleanField(db_index=True, default=True, help_text='Публиковать ролл через URN (URL-слаг). Если опубликовано, то и ролл можно будет адресовать по URL </i>/block/roll/content</i> и все связанные с ним единицы контента (и производные роллы в будущем). Если не опубликовано, то будет вызываться ошибка 404.', verbose_name='Вкл./Выкл. ролл')),
                ('iRollItemInPage', models.PositiveSmallIntegerField(blank=True, default=None, help_text='Сколько контентных единиц будет отображено в ленте на одной странице при пейджинации.', null=True, verbose_name='На странице')),
                ('szRollSortRule', models.CharField(blank=True, default='-dtCreate', help_text='Правило сортировки контента в ролле. Используются конструкции <b>order_by</b> для Django. Например: <i>dtCreate</i> или <i>-dtCreate</i>, или <i>szTitle</i>, или <i>-szTitle</i>…', max_length=128, null=True, verbose_name='Правило сортировки')),
                ('szRollFilterRule', models.CharField(blank=True, default='bPublish=True', help_text='Правило фильтрации контента в ролле. Используются конструкции <b>filter</b> для Django. Например: <i>dtCreate__gte=2019-01-01</i> или <i>dtCreate__lte=2019-01-01</i>…', max_length=128, null=True, verbose_name='Правило фильтрации')),
                ('szRollTitle', models.CharField(blank=True, help_text="Заголовок ролла. Отображается в шаблоне ролла в теге <i>title</i>.<br /><b style='color:red'>ТИПОГРАФИРУЕТСЯ!!</b> Может содержать HTML-теги.", max_length=255, null=True, verbose_name='Заголовок')),
                ('szRollText', models.TextField(blank=True, default='', help_text='Текст ролла (пояснения перед новостной лентой, блогом и пр.)</br><small>(разрешенHTML-код, будет обработан типографом, если типограф включен)</small>', null=True, verbose_name='Шаблон')),
                ('szRollRedirectTo', models.CharField(blank=True, default='', help_text="Иногда нужно, чтобы ролл (пункт меню) был редиректом на другой URL, например когдаролл снят с публикации (включен) и нужно перенаправить трафик.<br/><small>допустимы как внутренние URL-ссылки от корня сайта '/………', так и внешние URI-ссылки 'http://………'</small>", max_length=500, null=True, verbose_name='Редирект на')),
                ('dtRollCreate', models.DateTimeField(auto_now_add=True, verbose_name='Дата Создания')),
                ('dtRollTimeStamp', models.DateTimeField(auto_now=True, verbose_name='Штамп времени')),
                ('kDefaultContentTemplate', models.ForeignKey(blank=True, db_constraint=False, default=None, help_text="Шаблон (по умолчанию) который будет использован для типовых единиц контента в этом ролле.<br /><b style='color:red'>ПОДУМАЙТЕ ПЕРЕД ТЕМ КАК ИЗМЕНЯТЬ!!</br>Для любой единицы контента шаблон можно будет переназначить (например, когда вы делаете спец-страницы с уникальным дизайном).</b>", null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='kContentTemplate', to='roll_cms.tbtemplate', verbose_name='Шаблон Контента')),
                ('kRollImgPreview', filer.fields.file.FilerFileField(blank=True, help_text='Картинка-превью или любая заголовочная картинка. Например, для фон под заголовком, логотип брендирования и т.п.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='preview', to='filer.file', verbose_name='Ролл-Превью')),
                ('kRollTemplate', models.ForeignKey(blank=True, db_constraint=False, default=None, help_text="Шаблон отвечающий за отображение списка контента для категории.<br /><b style='color:red'>ПОДУМАЙТЕ ПЕРЕД ТЕМ КАК ИЗМЕНЯТЬ!!</b>", null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='kRollTemplate', to='roll_cms.tbtemplate', verbose_name='Шаблон ролла')),
            ],
            options={
                'verbose_name': '[…Ролл (список)]',
                'verbose_name_plural': '[…Роллы (списки)]',
                'ordering': ['id'],
            },
        ),
    ]