# -*- coding: utf-8 -*-
from django.shortcuts import render, HttpResponseRedirect
from django.template.exceptions import TemplateDoesNotExist
from django.db.models import QuerySet
from django.template import loader
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.http import Http404  # , request
from django.utils.timezone import now
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError
from typing import Optional, Dict
from roll_cms.models import TbTemplate, TbMenu, TbMenuPoint, TbRoll, TbItem
from roll_cms.add_function import *
import re


def get_context_for_menu(q_menu: QuerySet = None, menu_id: int = None, processed_menu: set = None) -> Optional[dict]:
    """ Получение контекста для меню

    :param q_menu: QuerySet c записью из TbMenu -- меню, для которого надо собрать контекст.
    :param menu_id: ID меню, для которого надо собрать контекст (не используется, если получено значение "menu").
    :param processed_menu: Множество обработанных меню (для избежания зацикливания вложенных меню).
    :param var : Переменная, которая будет использована для передачи контекста в шаблон.
    :return context: Контекст для меню.
    """
    # Контекст меню может содержать в себе пункты (роллы, элементы) и другие меню:
    #     { "__menu_name__": "Техническое название меню",
    #       "__menu_id__": "ID меню",
    #       "menu": [ {'bPointPublish': True,
    #                 'szPointName': "пункт меню для ролла или элемента",
    #                 'szPointTitle': "HTML, для оформления пункта меню",
    #                 'szPointUtlTo': "url пункта меню",\
    #                 },
    #                 ...
    #                 ...
    #                 {"__menu_name__": "Вложенное меню: техническое название меню",
    #                  "__menu_id__": "Вложенное меню: id меню",
    #                  "include": "<div>html-код вложенного меню</div>"
    #                 },
    #                 ...
    #               ]
    #     }
    if menu_id is None and q_menu is None:
        # Не передано ни ID меню, ни само меню, невозможно собрать контекст.
        return None
    if processed_menu is None:
        # Множество обработанных меню (для избежания зацикливания вложенных меню).
        processed_menu = set()
    if q_menu is None:
        try:
            # Нет QuerySet для "сборки" меню. Получим его из базы.
            q_menu = TbMenu.objects.get(pk=menu_id)
        except TbMenu.DoesNotExist:
            # Меню не найдено
            return None
    if menu_id is None:
        # Нет ID меню, получим его из QuerySet
        menu_id = q_menu.id
    if menu_id in processed_menu:
        # Меню уже обработано, пропускаем его, чтобы избежать вечного цикла.
        return None
    processed_menu.add(menu_id)
    context = {"__menu_id__": q_menu.id,
               "__menu_name__": q_menu.szMenuName,
               }
    points_list = list()
    # Получим все пункты меню для данного шаблона
    try:
        qs_menu_points = TbMenuPoint.objects.filter(kMenu_id=q_menu.id).order_by("iPointSort")
        for point in qs_menu_points:
            url_to = include = None
            # Добавим пункт меню в контекст
            if point.szPointUtlTo is not None and point.szPointUtlTo.strip():
                # Этот пункт просто ссылка (внешняя или внутренняя)
                url_to = point.szPointUtlTo
            elif point.kPoint2Roll_id is not None:
                # Этот пункт меню ведет на ролл
                url_to = f"/{URL_PREFIX_ROLL}{point.kPoint2Roll_id}-{point.kPoint2Roll.szRollSlug}"
            elif point.kPoint2Item_id is not None:
                # Этот пункт меню ведет на элемент
                url_to = f"/{URL_PREFIX_ITEM}{point.kPoint2Item_id}-{point.kPoint2Item.szSlug}"
            elif point.kPoint2Menu_id is not None:
                # Этот пункт меню требует включить другое меню
                # И да! Это вызывает рекурсию и кучу дополнительных запросов к базе! Все это медленно!
                # А меню, на сайте обычно на каждой странице!! Так что спасайтесь кешированием встроенным в Django,
                # или используйте кеш-шаблоны, которые есть в меню RollCMS (см. админку и читай документацию).
                include = render_to_string(template_name=point.kPoint2Menu.kMenuTemplateFrom.szFileName,
                                           context={
                                               point.kPoint2Menu.kMenuTemplateFrom.szVar:
                                                   get_context_for_menu(menu_id=point.kPoint2Menu_id)
                                           })
            else:
                # Неизвестный тип пункта меню
                pass
            points_list.append({
                'id': point.id,
                'bPointPublish': point.bPointPublish,
                'szPointName': point.szPointName,
                'szPointTitle': point.szPointTitle,
                'szPointUtlTo': url_to,
                'include': include
            })
        context.update({"menu": points_list})
        return context
    except TbMenuPoint.DoesNotExist:
        # print(f"Пункты меню для меню c id={q_menu.kMenu_id} не найдены.")
        return None


def get_context_for_roll(q_roll: QuerySet = None, roll_id: int = None, processed_roll: set = None) -> Optional[QuerySet]:
    """ Получение контекста для ролла

    :param q_roll: QuerySet c записью из TbRoll -- ролл, для которого надо собрать контекст.
    :param roll_id: ID ролла, для которого надо собрать контекст (не используется, если получено значение "q_roll").
    :param processed_roll: Множество обработанных роллов (для избежания зацикливания вложенных роллов).
    :param var : Переменная, которая будет использована для передачи контекста в шаблон.
    :return context: Контекст для ролла.
    """
    if roll_id is None and q_roll is None:
        # Не передано ни ID ролла, ни сам ролл, невозможно собрать контекст.
        return None
    if processed_roll is None:
        # Множество обработанных роллов (для избежания зацикливания вложенных роллов).
        processed_roll = set()
    if q_roll is None:
        try:
            # Нет QuerySet для "сборки" ролла. Получим его из базы.
            q_roll = TbRoll.objects.get(pk=roll_id)
        except TbRoll.DoesNotExist:
            # Ролл не найден
            return None
    filter_args_value = dict()
    args_value = q_roll.szRollFilterRule.split(",") if q_roll.szRollFilterRule is not None else None
    for pair in args_value:
        try:
            key, value = pair.split("=")
            value = eval(value)
        except:
            # Не удалось разобрать пару ключ=значение или ошибка eval(value)
            continue
        filter_args_value.update({key: value})
    # Добавим в словарь пару ключ-значение 'kRoll=q_roll.id'
    filter_args_value['kRoll'] = q_roll.id
    # Используем возможность вызова .order_by() в ORM Django без аргументов (это сбрасывает более ранние сортировки)
    order_by_args = q_roll.szRollSortRule.split(",") if q_roll.szRollSortRule is not None else None
    # добавим в QuerySet q_roll все элементы, которые соответствуют фильтрации и сортировке (и срез)
    q_roll.items = TbItem.objects.filter(**filter_args_value).order_by(*order_by_args)[:q_roll.iRollItemInPage]
    return q_roll


def gather_template_context(template_name: str, processed_var_context: dict = None,
                            processed_template_var: dict = None) -> Optional[dict]:
    """ Собирает контекст для шаблона

    :param template_name: имя шаблона
    :param processed_var_context: ранее полученный контекст -- {'var': 'context'}
    :param processed_template_var: ранее обработанные шаблоны -- {'template_name': 'var'}
    :return response: исходящий http-ответ
    """
    if processed_var_context is None:
        processed_var_context = dict()
    if processed_template_var is None:
        processed_template_var = dict()

    if template_name in processed_template_var:
        # Шаблон уже был обработан, пропускаем его, чтобы избежать вечного цикла.
        # Достаточно простого return, но мы вернем пустое содержимым со специальным статусом 204 (No Content).
        return processed_var_context
    try:
        # Получаем исходный текст шаблона из базы (так быстрее, чем читать файлы)
        q1_template = TbTemplate.objects.get(szFileName=template_name)
        # Проверим, что для данного шаблона нужно передать контекст
        if q1_template.szVar is None or not q1_template.szVar.strip():
            # Для этого шаблона контекст не нужен, а заодно q1_template.szVar проверит наличие QuerySet или "упадёт"
            processed_template_var.update({template_name: None})
            # return processed_var_context
    except TbTemplate.DoesNotExist:
        # Шаблон не найден в базе, попробуем найти его в файловой системе и перенести в базу.
        path_to_template = f"{TEMPLATES[1]['DIRS'][0]}/{template_name}"
        if template_name.lower().endswith((".jinja2", ".j2", ".jinja",)):
            path_to_template = f"{TEMPLATES[0]['DIRS'][0]}/{template_name}"
        try:
            with open(path_to_template, "r", encoding="utf-8") as file:
                # Шаблон найден в файловой системе... получаем код шаблона...
                template_code = file.read()
                # ...найдём (или нет) переменную контекста в коде шаблона -- "{# RollCMS_var _переменная_ #}"
                match = re.search(pattern=r"{#\s+RollCMS_var\s+(\S+)\s+#}",
                                  string=template_code, flags=re.IGNORECASE)
                template_var = None if match is None else match.group(1)
                # ...найдём (или нет) описание в коде шаблона -- "{# RollCMS_description _описание_ #}"
                match = re.search(pattern=r"{#\s+RollCMS_description\s+(.+?)\s+#}",
                                  string=template_code, flags=re.IGNORECASE)
                template_description = f"from: \"{template_name}\"" if match is None else match.group(1)
                # ...и запишем шаблон в базу данных и. одновременно, получим QuerySet для дальнейшей работы
                q1_template = TbTemplate.objects.create(
                    szFileName=template_name, szJinjaCode=template_code,
                    szVar=template_var, szDescription=template_description
                )
        except FileNotFoundError:
            # Шаблон не найден ни в базе, ни в файловой системе. Беда!
            raise TemplateDoesNotExist(f"{path_to_template}")
    # Получим контекст для этого шаблона. В gather_template_context() присвоение контекстных переменных,
    # в первую очередь, осуществляется на основании директории (каталога), в котором расположен шаблон.
    # Контекст связанный с URL не учитывается (если он есть, то он должен был быть получен функцией снаружи).
    template_folder_name = q1_template.szFileName.split("/")[0]
    if template_folder_name in [FOLD_CASH_TEMPLATES, FOLD_BLOCK_TEMPLATES]:
        # Это шаблон блока или кэша. У них нет контекста.
        processed_template_var.update({template_name: None})
    elif template_folder_name == FOLD_MENU_TEMPLATES:
        # Это шаблон для создания меню. Получаем контекст меню из базы
        q_menu=TbMenu.objects.filter(kMenuTemplateFrom_id=q1_template.id).first()
        if q_menu is None:
            # В таблице TbMenu нет записи о меню, которое использует этот шаблон.
            processed_template_var.update({template_name: None})
        else:
            contex = get_context_for_menu(q_menu)
            processed_template_var.update({template_name: q1_template.szVar})
            processed_var_context.update({q1_template.szVar: contex})
    elif template_folder_name == FOLD_ROLL_TEMPLATES:
        # Это шаблон ролла (который . Получаем контекст ролла из базы
        # Это ролл, который встроен в шаблон
        q_roll = TbRoll.objects.filter(kRollTemplate_id=q1_template.id).first()
        if q_roll is None:
            # В таблице TbRoll нет записи о ролле, который использует этот шаблон.
            processed_template_var.update({template_name: None})
        else:
            # Надо учесть, что во встроенном ролле могут быть свои фильтрации, сортировки и т.п.
            # Найдем '{# RollCMS_Roll_ItemInPage _число_ #} -- число элементов во встроенном ролле (в коде шаблона)
            match = re.search(pattern=r"{#\s+RollCMS_RollItemIn\s+(\d+?)\s+#}",
                              string=q1_template.szJinjaCode, flags=re.IGNORECASE)
            if match is not None:
                # Это ролл с альтернативным числом элементов
                q_roll.iRollItemInPage = int(match.group(1))
            # Найдем '{# RollCMS_RollFilterRule _строка_ #} -- правило фильтрации для встроенного ролла (в коде шаблона)
            match = re.search(pattern=r"{#\s+RollCMS_RollFilterRule\s+(.+?)\s+#}",
                              string=q1_template.szJinjaCode, flags=re.IGNORECASE)
            if match is not None:
                # Это ролл с альтернативным правилом фильтрации
                q_roll.szRollFilterRule = match.group(1)
            # Найдем '{# RollCMS_RollSortRule _число_ #} -- правило сортировки для встроенного ролла (в коде шаблона)
            match = re.search(pattern=r"{#\s+RollCMS_RollSortRule\s+(.+?)\s+#}",
                              string=q1_template.szJinjaCode, flags=re.IGNORECASE)
            if match is not None:
                # Это ролл с альтернативным правилом сортировки
                q_roll.szRollSortRule = match.group(1)
            contex = get_context_for_roll(q_roll)
            processed_template_var.update({template_name: q1_template.szVar})
            processed_var_context.update({q1_template.szVar: contex})

        pass
    elif template_folder_name == FOLD_ITEM_TEMPLATES:
        # TODO: Это шаблон элемента. Получаем контекст элемента из базы
        pass
    else:
        # TODO: На самом деле можно найти контекст для любого шаблона... просто это дольше,
        #  и если один шаблон используется несколькими меню, роллами или элементами, то
        #  можно серьезно запутаться.
        pass
    # if q1_template.szVar in processed_var_context:
    #     # Хотя шаблон еще не обработан, но переменная szVar уже использована для передачи контекста.
    #     # Поднимаем исключение TemplateSyntaxError (а то может упасть, может не упасть... админ сайта напугается
    #     # и не поймёт, что это за ошибка).
    #     raise TemplateSyntaxError(f"Переменная \"{q1_template.szVar}\" в шаблоне \"{template_name}\""
    #                               f" уже использована для передачи контекста.", lineno=0)
    #     # return HttpResponse(status=204)
    # processed_template_var.update({template_name: q1_template.szVar})

    # Удаляем комментарии  {# ... #}, {% comment %} ... {% endcomment %}, и <!-- ... --> из шаблона
    template_without_comments = re.sub(
        pattern=r"({#.*?#}|{%\s*comment\s*%}.*?{%\s*endcomment\s*%}|<!--.*?-->)",
        repl='',
        string=q1_template.szJinjaCode,
        flags=re.DOTALL | re.IGNORECASE)
    # Находим все используемые через include и extends, производные шаблоны
    matches = re.findall(
        pattern=r"{%\s+(include|extends)\s+(['\"])(.*?)\2\s+%}",
        string=template_without_comments,
        flags=re.IGNORECASE
    )
    # Преобразование списка кортежей в список строк
    # match[2] соответствует третьей группе в регулярном выражении, которая содержит имя файла шаблона
    includes_and_extends = [match[2] for match in matches]
    for included_template in includes_and_extends:
        # Рекурсивный вызов gather_template_context() для вложенных шаблонов
        gather_template_context(included_template, processed_var_context, )
    return processed_var_context


def index(request: HttpRequest) -> HttpResponse:
    """ Тест индексной страницы

    :param
    :return response: исходящий http-ответ
    """
    try:
        context = gather_template_context(template_name="index.jinja2")
        return render(request, template_name="index.jinja2", context=context)
    except TemplateDoesNotExist as e:
        # Обработка ошибки отсутствия шаблона
        return HttpResponse(f"ОШИБКА RollCSM: не найден шаблон \"{e}\". Создайте его.", status=424)
    except TemplateNotFound as e:
        # Обработка ошибки отсутствия вложенного шаблона
        return HttpResponse(f"RollCSM не нашла производный шаблон \"{e}\". Создайте его.", status=424)


def _index(request: HttpRequest,
          urn_block: str = None,
          urn_roll: str = None,
          urn_content: str = None,
          page: int = 0) -> HttpResponse:
    """ Универсальный обработчик для всех страниц сайта

    :param request: входящий http-запрос
    :param urn_block: часть URL для выборки блоков (из таблицы TbBlock)
    :param urn_roll: часть URL для выборки роллов (из таблицы TbRoll)
    :param urn_content: часть URL для выборки контента (из таблицы TbContent)
    :param page: номер страницы (начиная с нуля) для выборки конкретной страницы роллов
    :return response: исходящий http-ответ
    """
    to_template = {"COOKIES": check_cookies(request),
                   "URN_BLOCK": urn_block,
                   "URN_ROLL": urn_roll,
                   "URN_CONTENT": urn_content,
                   "PAGE": page}
    if urn_block is None:
        # пришел запрос на главную страницу -- "/"
        template = "index.jinja2"  # шаблон
    elif urn_content is None:
        # Нет части URL заведующей за контент, значит это "чистый" ролл.
        # Сначала ПОЛУЧИМ ДАННЫЕ БЛОКА в q_block
        try:
            # найдём блок по части URL
            q_block = TbBlock.objects.get(szBlockSlug=urn_block)
            if q_block.bRollPublish:
                # блок опубликован к доступу через URL/URN
                template = q_block.kRollTemplate.szFileName
            else:
                # блок не опубликован, возвращаем 404
                raise Http404("Возможно, такая страница была, но сейчас её не существует!")
        except (TbBlock.DoesNotExist, TbBlock.MultipleObjectsReturned):
            raise Http404("Сто мартышек искали страницу, но её нет!")
        # ДАННЫЕ БЛОКА ПОЛУЧЕНЫ:
        # получим данные для ролла (ЗАГОЛОВОК РОЛЛА) в q_roll
        # и отправим данные ролла в шаблон через переменную приписанную к шаблону
        to_template.update({q_block.kRollTemplate.szVar: get_roll_data(q_block, urn_roll, page)})
    else:
        # есть часть URL заведующая за контент, значит надо готовить данные для контента
        # ПОКА ЭТА ЧАСТЬ НЕ ГОТОВА
        template = "__"
    # поиск в шаблоне "{% include 'file' %}" и рекурсивный обход всех шаблонов
    # включенных в шаблон
    # {% include "***" %} и {% extends '***' %}
    sup_sub_template_list = get_sub_sup_template(template)
    # пробежим по всем найденным шаблонам
    for tmpl in sup_sub_template_list:
        # если шаблон текущей -- пропускаем
        if tmpl == template:
            continue
        # найдем блок, который использует этот шаблон для отображения ролла
        # если таких блоков (использующих один и тот же шаблон) несколько,
        # то возьмём с самым маленьким ID!!!
        # ВАЖНО: если вы хотите использовать один и тот же шаблон для разных блоков,
        #        то имейте в виду, что для роллов из вложенных шаблонов может
        #        попасть не то что вы ожидаете!!!
        q_block_r = TbBlock.objects.filter(kRollTemplate__szFileName=tmpl).order_by("id").first()
        if q_block_r is not None:
            # Если блок найден, то получим данные для ролла (т.к. это ролл производного
            # шаблона, т.е. он встроен в какую-то другую страничку, то пейджинатор
            # на производном ролле смысла не имеет. Если он есть в шаблоне -- то, хрен
            # знает как он должен работать! Данные для паджинаторов производных роллов
            # не формируются. Лучше для производных роллов использовать специальные
            # шаблоны без паджинторов!!!
            to_template.update({q_block_r.kRollTemplate.szVar: get_roll_data(q_block_r, urn_roll)})
            continue
        # не нашли подходящий ролл, попробуем найти контнент-блок
        q_block_c = TbBlock.objects.filter(kContentTemplate__szFileName=tmpl).order_by("id").first()
        if q_block_c is not None:
            # Если контент найден, то получим данные этого контента
            print("Найден контент для шаблона: " + tmpl)
            continue

    print("template =", template)
    print("sup_sub_template_list =", sup_sub_template_list)
    print("to_template =", to_template)

    # to_template.update = {"COOKIES": check_cookies(request)}
    return render(request, template, to_template)
