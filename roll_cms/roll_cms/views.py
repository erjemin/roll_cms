# -*- coding: utf-8 -*-
from django.shortcuts import render, HttpResponseRedirect
from django.template.exceptions import TemplateDoesNotExist
from django.template import loader
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.http import Http404  # , request
from django.utils.timezone import now
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError
from roll_cms.models import TbTemplate
from roll_cms.add_function import *
import re


def render_wrap(request: HttpRequest, template_name: str, context: dict, processed_templates: set = None) -> HttpResponse:
    """ Обертка для функции render

    :param request: входящий http-запрос
    :param template_name: имя шаблона
    :param context: контекст для шаблона
    :param processed_templates: список уже обработанных шаблонов (бля избегания вечного цикла)
    :return response: исходящий http-ответ
    """
    if processed_templates is None:
        processed_templates = set()
    if template_name in processed_templates:
        # Шаблон уже был обработан, пропускаем его, чтобы избежать вечного цикла.
        # Достаточно простого return, но мы вернем пустое содержимым со специальным статусом 204 (No Content).
        HttpResponse(status=204)
    processed_templates.add(template_name)
    # if template_name.endswith(('.jinja2', '.j2', '.jinja')):
    #     # Это Jinja2 шаблон

    print("template_name =", template_name)
    try:
        # Получаем исходный текст шаблона из базы (так быстрее, чем читать файлы)
        q1_template = TbTemplate.objects.get(szFileName=template_name)
        # Получим контекст для этого шаблона. В render_wrap присвоение контекстных переменных осуществляется только
        # на основании каталога, в котором находится шаблон. Контекст связанный с URL не учитывается.
        # TODO: Сделай это!

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
            print("included_template =", included_template)
            render_wrap(request, included_template, context, processed_templates)
    except TbTemplate.DoesNotExist:
        # Шаблон не найден
        # TODO: Проверить наличие шаблона в файловой системе, и если он там есть, то добавить его в базу. Т.о. можно
        #       будет распространять готовые приложения. При первом обращении все шаблоны сами добавятся в базу.
        print(f"Шаблон в базе не обнаружен \"{template_name}\". Создайте его.")
        return HttpResponse(content=f"Вложенный шаблон в базе не обнаружен \"{template_name}\". Создайте его.", status=424)

    # return render(request, template_name, context)
    return HttpResponse(f"\"{template_name}\".", status=424)
    # else:
    #     # Это Django шаблон
    #     return HttpResponse(f"RollCSM пока не работает с Jango-шаблонами \"{template_name}\".", status=424)


def index(request: HttpRequest) -> HttpResponse:
    """ тест индексной страницы

    :param
    :return response: исходящий http-ответ
    """
    try:
        return render_wrap(request, "index.jinja2", {})
    except TemplateDoesNotExist as e:
        # Обработка ошибки отсутствия шаблона
        return HttpResponse(f"RollCSM не нашла шаблон для ролла/контента \"{e}\". Создайте его.", status=424)
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
