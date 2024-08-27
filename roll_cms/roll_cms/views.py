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
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError, UndefinedError
from typing import Optional, Dict
from roll_cms.models import TbTemplate, TbMenu, TbMenuPoint, TbRoll, TbItem
from roll_cms.add_function import *
import re


def handler404(request: HttpRequest, exception: str) -> HttpResponse:
    """ Обработчик ошибки 404

    :param request: входящий http-запрос
    :param exception:   сообщение с причиной ошибки
    :return response: исходящий http-ответ
    """
    response = render(request, template_name="404.html", context={"MSG": exception})
    response.status_code = 404
    return response


def handler500(request: HttpRequest) -> HttpResponse:
    """ Обработчик ошибки 500

    :param request: входящий http-запрос
    :return response: исходящий http-ответ
    """
    response = render(request, template_name="500.html", context={})
    response.status_code = 500
    return response


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
        except:     # except (ValueError, KeyError, SyntaxError, AttributeError):
            # Не удалось разобрать пару ключ=значение или ошибка eval(value)
            continue
        filter_args_value.update({key: value})
    # Добавим в словарь пару ключ-значение 'kRoll=q_roll.id'
    filter_args_value['kRoll'] = q_roll.id
    # Используем возможность вызова .order_by() в ORM Django без аргументов (это сбрасывает более ранние сортировки)
    order_by_args = q_roll.szRollSortRule.split(",") if q_roll.szRollSortRule is not None else None
    # добавим в QuerySet q_roll все элементы, которые соответствуют фильтрации и сортировке (и срез)
    if q_roll.iRollItemInPage is None or q_roll.iRollItemInPage < 1:
        # В ролле не указано количество элементов на странице, поэтому берем все элементы
        q_roll.items = TbItem.objects.filter(**filter_args_value).order_by(*order_by_args)
    else:
        q_roll.items = TbItem.objects.filter(**filter_args_value).order_by(*order_by_args)[:q_roll.iRollItemInPage]
    return q_roll


def gather_template_context(template_name: str, processed_var_context: dict = None,
                            processed_template_var: dict = None) -> None:
    """ Собирает контекст для шаблона

    :param template_name: имя шаблона
    :param processed_var_context: ранее полученный контекст -- {'var': 'context'}
    :param processed_template_var: ранее обработанные шаблоны -- {'template_name': 'var'}
    :return response: None (результат возвращается в переменных processed_var_context и processed_template_var)
    """
    if processed_var_context is None:
        processed_var_context = dict()
    if processed_template_var is None:
        processed_template_var = dict()

    # Даже если контектст для этого шаблона уже собран (например, при обработке по URL), могут быть вложенные шаблоны,
    # которые тоже потребуют контекста. Поэтому, получим код шаблона для поиска вложенных шаблонов. Это, безусловно,
    # замедлит работу, но благодаря кешированию на уровне Django (в продакшн) не должно стать проблемой.
    try:
        # Получаем исходный текст шаблона из базы (так быстрее, чем читать файлы)
        q1_template = TbTemplate.objects.get(szFileName=template_name)
        # Проверим, что для данного шаблона нужно передать контекст
        if q1_template.szVar is None or not q1_template.szVar.strip():
            # Для этого шаблона контекст не нужен, а заодно q1_template.szVar проверит наличие QuerySet или "упадёт"
            processed_template_var.update({template_name: None})
            # print(f"Шаблон есть в БД, но нет szVar: processed_template_var = {processed_template_var}")
            # print(f"Нет szVar, некуда положить контекст, а значит и нечего этот контекст получать, выходим.")
            # return
    except TbTemplate.DoesNotExist:
        # Шаблон не найден в базе, попробуем найти его в файловой системе и перенести в базу.
        # print(f"Шаблона \"{template_name}\" нет в базе. Попробуем найти его в файловой системе.")
        path_to_template = os.path.join(TEMPLATES[1]['DIRS'][0], template_name)
        if template_name.lower().endswith((".jinja2", ".j2", ".jinja",)):
            path_to_template = os.path.join(TEMPLATES[0]['DIRS'][0], template_name)
        # print(f"Полный путь к файлу шаблона: \"{path_to_template}\"")
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
                # print(f"Шаблона нет в базе, но он есть в файловой системе. Записали его в базу: {q1_template}")
                if q1_template.szVar is None:
                    processed_template_var.update({template_name: None})
                    # print(f"Шаблон есть в файле, но нет szVar: processed_template_var = {processed_template_var}")
                    # print(f"Нет szVar, некуда положить контекст, а значит и нечего этот контекст получать, выходим.")
                    # return
        except FileNotFoundError:
            # Шаблон не найден ни в базе, ни в файловой системе. Беда!
            raise TemplateDoesNotExist(f"{path_to_template}")

    if template_name not in processed_template_var:
        # Шаблон еще не был обработан, нужно собрать контекст для него.
        # print(f"Нужно получить контекст для шаблона: \"{template_name}\" в переменную: \"{q1_template.szVar}\"")
        # Получим контекст для этого шаблона. В gather_template_context() присвоение контекстных переменных,
        # в первую очередь, осуществляется на основании директории (каталога), в котором расположен шаблон.
        # Контекст связанный с URL не учитывается (если он есть, то он был получен функцией снаружи).
        template_folder_name = q1_template.szFileName.split("/")[0]
        if template_folder_name in [FOLD_CASH_TEMPLATES, FOLD_BLOCK_TEMPLATES]:
            #
            # Это шаблон блока или кэша. У них нет контекста.
            # print(f"Это шаблон блока или кэша: \"{template_name}\". Такие шаблоны не имеют контекста.")
            processed_template_var.update({template_name: None})
        elif template_folder_name == FOLD_MENU_TEMPLATES:
            #
            # Это шаблон для создания меню. Получаем контекст меню из базы
            # print(f"Это шаблон для создания меню: \"{template_name}\"")
            processed_template_var.update({template_name: q1_template.szVar})
            q_menu = TbMenu.objects.filter(kMenuTemplateFrom_id=q1_template.id).first()
            if q_menu is None:
                # В таблице TbMenu нет записи о меню, которое использует этот шаблон, а значит и нет контекста.
                processed_var_context.update({q1_template.szVar: None})
                # print(f"Контекста для меню \"{q1_template.szVar}\" не будет.")
            else:
                contex = get_context_for_menu(q_menu)
                processed_var_context.update({q1_template.szVar: contex})
                # print(f"Контекст для меню \"{q1_template.szVar}\": {contex}")
        elif template_folder_name == FOLD_ROLL_TEMPLATES:
            # Это шаблон ролла. Получаем контекст ролла из базы
            # Это ролл, который встроен в шаблон
            # print(f"Это шаблон для создания ролла: \"{template_name}\"")
            processed_template_var.update({template_name: q1_template.szVar})
            q_roll = TbRoll.objects.filter(kRollTemplate_id=q1_template.id).first()
            if q_roll is None:
                # В таблице TbRoll нет записи о ролле, который использует этот шаблон.
                # print(f"Ролл \"{q1_template.szVar}\" не найден. А значит и контекста для него невозможно получить.")
                processed_var_context.update({q1_template.szVar: None})
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
                contex = get_context_for_roll(q_roll=q_roll)
                # print(f"Контекст для ролла \"{q1_template.szVar}\": {contex}")
                processed_var_context.update({q1_template.szVar: contex})

            pass
        elif template_folder_name == FOLD_ITEM_TEMPLATES:
            print(f"Это шаблон для создания элемента: \"{template_name}\"")
            # TODO: Это шаблон элемента. Получаем контекст элемента из базы
            pass
        else:
            # TODO: На самом деле можно найти контекст для любого шаблона... просто это дольше,
            #  и если один шаблон используется несколькими меню, роллами или элементами, то
            #  можно серьезно запутаться.
            pass
        # print(f"Общий контекст: processed_var_context = {processed_var_context}")
        # if q1_template.szVar in processed_var_context:
        #     # Хотя шаблон еще не обработан, но переменная szVar уже использована для передачи контекста.
        #     # Поднимаем исключение TemplateSyntaxError (а то может упасть, может не упасть... админ сайта напугается
        #     # и не поймёт, что это за ошибка).
        #     raise TemplateSyntaxError(f"Переменная \"{q1_template.szVar}\" в шаблоне \"{template_name}\""
        #                               f" уже использована для передачи контекста.", lineno=0)
        #     # return HttpResponse(status=204)
        # processed_template_var.update({template_name: q1_template.szVar})

    # Теперь нужно найти все вложенные шаблоны и получить контекст и для них.
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
        # print(f"===\tРекурсивный вызов gather_template_context() для вложенного шаблона: \"{included_template}\"")
        # print(f"---\tprocessed_var_context = {processed_var_context}")
        # print(f"---\tprocessed_template_var = {processed_template_var}")
        gather_template_context(template_name=included_template,
                                processed_var_context=processed_var_context,
                                processed_template_var=processed_template_var)
    return


def index(request: HttpRequest) -> HttpResponse:
    """ Тест индексной страницы

    :param request: http-запрос
    :return response: исходящий http-ответ
    """
    try:
        # processed_template_var: dict = None
        context = dict()
        gather_template_context(template_name="index.jinja2", processed_var_context=context)
        # print(f"\n=====\n Общий контекст для шаблона \"index.jinja2\": {context}")
        context.update({"__ALL_ROLLCMS_CONTEXT": context})
        return render(request, template_name="index.jinja2", context=context)
    except TemplateDoesNotExist as e:
        # Обработка ошибки отсутствия шаблона
        return HttpResponse(f"ОШИБКА RollCSM: не найден шаблон \"{e}\". Создайте его.", status=424)
    except TemplateNotFound as e:
        # Обработка ошибки отсутствия вложенного шаблона
        return HttpResponse(f"RollCSM не нашла производный шаблон \"{e}\". Создайте его.", status=424)


def universal_processor(request: HttpRequest, url_chain: str) -> HttpResponse:
    """ Универсальный обработчик

    :param request: http-запрос
    :param url_chain: URN (полная цепочка .../.../... и т.д.)
    :return response: исходящий http-ответ
    """
    processed_var_context = dict()
    processed_template_var = dict()
    template_name = str()
    var = str()
    breadcrumbs = url_chain.split("/")
    last_of_breadcrumbs = breadcrumbs[-1]
    # match = re.search(pattern=rf"({URL_PREFIX_ROLL}|{URL_PREFIX_ITEM}|{URL_PREFIX_TAGG})(\d+)-\S+",
    #                   string=last_of_breadcrumbs)
    match = re.search(pattern=rf"({URL_PREFIX_ROLL}|{URL_PREFIX_ITEM})(\d+)-\S+|{URL_PREFIX_TAGG}-(\S+)",
                      string=last_of_breadcrumbs)
    if match.group(1) == URL_PREFIX_ROLL:
        #
        # Это ролл вызванный по URN
        #
        # print(f"Это URN для отображения ролла с ID = {match.group(2)}")
        roll_id = int(match.group(2))
        try:
            q_roll = TbRoll.objects.get(pk=roll_id)
            if q_roll.bRollPublish is False:
                # Ролл не опубликован
                return HttpResponse(content=f"RollCSM не может отобразить ролл c id={roll_id}, т.к. он не опубликован.",
                                    status=424)
            template_name = q_roll.kRollTemplate.szFileName  # т.к. в Django запрос "ленивые", то так тоже работает.
            var = q_roll.kRollTemplate.szVar
        except TbRoll.DoesNotExist as e:
            # Ролл не найден
            return HttpResponse(content=f"RollCSM не нашла ролла c id={roll_id}.<br />"
                                        f"Создайте его через панель администрирования.<br /> <br />{e}", status=424)
        except (AttributeError, TemplateDoesNotExist, TemplateNotFound, ) as e:
            # Ролл найден, но шаблон не найден
            # TODO: Возможно стоит сделать проверку, есть-ли шаблон в файловой системе и перенести его в базу.
            #       Для этого на придумать способ автоматического наименования шаблонов (как-то связанного со Slug.
            #       Но предварительно надо придумать способ автоматической заливки данных в базу (иначе, без данных базе
            #       нельзя будет даже понять, что есть такой ролл и надо создать его шаблон).
            return HttpResponse(content=f"RollCSM не нашла шаблон для ролла c id={roll_id}.<br />"
                                        f"Создайте его.<br /> <br />{e}", status=424)
        processed_template_var.update({template_name: var})
        if var is None or not var.strip():
            # У этого ролла нет переменой для передачи контекста, а значит и контекст не нужен!
            # print(f"Для ролла \"{roll_id}\" контекст не нужен.")
            pass
        else:
            breadcrumbs[-1] = f"{URL_PREFIX_ROLL}{roll_id}-{q_roll.szRollSlug}"
            context = get_context_for_roll(q_roll=q_roll)
            processed_var_context.update({var: context})

    elif match.group(1) == URL_PREFIX_ITEM:
        #
        # Это элемент вызванный по URN
        #
        # print(f"Это URN для отображения элемента с ID = {match.group(2)}")
        item_id = int(match.group(2))
        try:
            q_item = TbItem.objects.get(pk=item_id)
        except TbItem.DoesNotExist as e:
            # Элемент не найден
            return HttpResponse(content=f"RollCSM не нашла элемент c id={item_id}.<br />"
                                        f"Создайте его через панель администрирования.<br /> <br />{e}", status=424)
        if (q_item.bPublish is False or (q_item.tdStart and q_item.tdStart > now()) or
                (q_item.tdStop and q_item.tdStop < now())):
            # Элемент не опубликован
            return HttpResponse(content=f"RollCSM не может отобразить элемент c id={item_id}, т.к. он не"
                                        f"опубликован или срок его публикации истек или еще не наступил.",
                                status=424)
        # print(f"Элемент \"{q_item.szName}\" опубликован.")
        try:
            template_name = q_item.kTemplate.szFileName
            var = q_item.kTemplate.szVar
        except AttributeError:
            if template_name is None or not template_name.strip():
                # То что у элемента-контента нет индивидуального шаблона -- нормальная ситуация. Шаблоны
                # у элементов-контента обычно задается в родительском ролле. Но если элемент включен в несколько
                # роллов, то может произойти коллизия шаблонов, и выберем один (первый по сортировкам
                # по умолчанию заданным в моделях).
                rolls_that_include_the_item = q_item.kRoll.all()
                # Проверить, пустой ли QuerySet
                if not rolls_that_include_the_item.exists():
                    return HttpResponse(content=f"RollCSM не нашла для элемента c id={item_id} ни индивидуального"
                                                f" шаблона, ни контент-шаблона наследуемого из ролла.<br />"
                                                f"Привяжите элемент к роллу с контент-шаблону или задайте"
                                                f" через панель администрирования или .",
                                        status=424)
                for roll in rolls_that_include_the_item:
                    if roll.kDefaultContentTemplate and roll.kDefaultContentTemplate.szFileName:
                        template_name = roll.kDefaultContentTemplate.szFileName
                        var = roll.kDefaultContentTemplate.szVar
                        break
                if template_name is str():      # Если имя шаблона пустая строка, то есть шаблон не найден
                    # Не удалось найти шаблон для элемента
                    return HttpResponse(content=f"RollCSM не нашла для элемента c id={item_id} ни индивидуального"
                                                f" шаблона, ни контент-шаблона наследуемого из ролла.<br />"
                                                f"Привяжите элемент к роллу с контент-шаблону или задайте"
                                                f" через панель администрирования или .",
                                        status=424)
        # print(f"Шаблон для элемента: \"{template_name}\"")
        processed_template_var.update({template_name: var})
        if var:
            # У этого элемента в шаблоне есть переменная для передачи контекста, а значит нужно получить контекст.
            breadcrumbs[-1] = f"{URL_PREFIX_ITEM}{item_id}-{q_item.szSlug}"
            # Возможно стоит вызвать функцию для получения контекста для элемента
            # context = get_context_for_item(q_item=q_item)
            # Но мы его уже получили. Т.к. пока функция get_context_for_item() не реализована, то
            # просто добавим элемент в контекст.
            processed_var_context.update({var: q_item})
            # print(f"processed_template_var = {processed_template_var}")
            # print(f"processed_var_context = {processed_var_context}")

    elif match.group(1) == URL_PREFIX_TAGG:
        #
        # Это тег
        #
        return HttpResponse(content=f"RollCSM пока не обрабатывает теги", status=424)

    # теперь нужно собрать остальной контекст из вложенных в template_name шаблонов.
    gather_template_context(template_name=template_name,
                            processed_var_context=processed_var_context,
                            processed_template_var=processed_template_var)
    try:
        # Для отладки. Чтобы видеть весь контекст в шаблоне --+
        #                                                     |
        processed_var_context.update({"__ALL_ROLLCMS_CONTEXT": processed_var_context})
        # TODO: Надо сделать обработку breadcrumbs (хлебных крошек), чтобы в шаблон передать корректный список словарей
        #       с именем и url каждой "крошки"
        #
        url_chain = f"/{'/'.join(breadcrumbs)}"   # исправленная последнее звено цепочки URL (c '/' в начале)
        # print(url_chain)
        processed_var_context.update({"__URL_CHAIN": url_chain,
                                      "__URL_PREFIX_ROLL": URL_PREFIX_ROLL,
                                      "__URL_PREFIX_ITEM": URL_PREFIX_ITEM,
                                      "__URL_PREFIX_TAGG": URL_PREFIX_TAGG,
                                      })
        return render(request, template_name=template_name, context=processed_var_context)
    except UndefinedError as e:
        # Неизвестная ошибка
        return HttpResponse(content=f"RollCSM не может отобразить шаблон: \"{template_name}\"<br />"
                                    f"Ошибка сборки контекста вложенных шаблонов.<br />"
                                    f"<br /> <br />{e}", status=424)
