# -*- coding: utf-8 -*-
# ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ ПРОЕКТА ROLL_CMS (не вьшки)

from roll_cms.settings import *
from django.http import HttpRequest, HttpResponse
from django import forms
from django.db import models
from datetime import datetime
from roll_cms.settings import *
import random
import regex
import re
import html
import pytils


def check_cookies(request: HttpRequest) -> bool:
    # проверка, что посетитель согласился со сбором данных через cookies
    if request.COOKIES.get('cookie_accept'):
        return False
    return True


def log_p(msg: str = "", status: str = "NO_STATUS", add: str = "") -> str:
    """
    Возвращает строку лога (и печатает в stdout (print) в режиме DEBUG

    :param msg: str     -- основное сообщение лога
    :param status: str  -- статус: "OK", "ERROR"  и т.д.
    :param add: str     -- дополнительная информация в лог
    :return: str        -- лог-строка
    """
    log_string = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')} -- {status} -- {msg} -- {add}"
    if DEBUG:
        # во время разработки выводим логи в stdout
        print(log_string)
    else:
        # TODO: в продакшене c логами будем делать что-то другое, например вообще ничего не делать
        pass
    return log_string


def safe_html_special_symbols(s: str) -> str:
    """ Очистка строки от HTML-разметки типографа

        :param s:   строка которую надо очистить
        :return: str:
    """
    # очистка строки от некоторых спец-символов HTML
    result = s.replace('&shy;', '­')
    result = result.replace('<span class="laquo">', '')
    result = result.replace('<span style="margin-right:0.44em;">', '')
    result = result.replace('<span style="margin-left:-0.44em;">', '')
    result = result.replace('<span class="raquo">', '')
    result = result.replace('<span class="point">', '')
    result = result.replace('<span class="thinsp">', ' ')
    result = result.replace('<span class="ensp">', '')
    result = result.replace('</span>', '')
    result = result.replace('&nbsp;', ' ')
    result = result.replace('&laquo;', '«')
    result = result.replace('&raquo;', '»')
    result = result.replace('&hellip;', '…')
    result = result.replace('<nobr>', '')
    result = result.replace('</nobr>', '')
    result = result.replace('&mdash;', '—')
    result = result.replace('&#8470;', '№')
    result = result.replace('<br />', ' ')
    result = result.replace('<br>', ' ')
    return result


def hyphenation_in_word(s: str, sep: str = "") -> str:
    """ Расстановка переносов в слове
    рецепт: https://ru.stackoverflow.com/questions/900660/Расстановка-переносов-в-русских-словах

    :param s:     Слово в котором надо расставить переносы
    :param sep:   Символ переноса
    :return: str: Слово с расставленными переносами
    """
    # расстановка переносов в слове
    def is_vow(let: str) -> bool:
        """ Проверка, что символ - гласная буква """
        return let.upper() in ['А', 'О', 'И', 'Е', 'Ё', 'Э', 'Ы', 'У', 'Ю', 'Я']

    def is_cons(let: str) -> bool:
        """ Проверка, что символ - согласная буква """
        return let.upper() in ['Б', 'В', 'Г', 'Д', 'Ж', 'З', 'К', 'Л', 'М', 'Н', 'П', 'Р', 'С', 'Т', 'Ф', 'Х', 'Ц',
                               'Ч', 'Ш', 'Щ']

    def vow_inds(wrd: str):
        """ Поиск индексов гласных букв в слове """
        return [i for i in range(len(wrd) - 2) if is_vow(wrd[i])]

    word = s
    vow_indices = vow_inds(word)
    if vow_indices and vow_indices[0] + 2 < len(word):
        for ind in vow_indices:
            ind += 1
            if (is_cons(word[ind]) or word[ind] in 'йЙ') and not is_vow(word[ind + 1]):
                ind += 1
            if len(word[:ind]) == 1:  # не даем отделять единичные гласные
                sep = ''
            if len(word) > 3 and word[ind] in 'ьЬЪъ':
                if word[-1] in 'ьЬЪъ':
                    sep = ''
                ind += 1

            return word[:ind] + sep + hyphenation_in_word(word[ind:])
    # print(f'Варианты расстановки переносов слова "{s}" - [ {word} ]')
    return word


def hyphenation_in_text(text: str, min_len_word_hyphenation: int = 14, sep: str = "") -> str:
    """ Расстановка переносов в тексте

        :param text: строка, которую надо обработать
        :param min_len_word_hyphenation: минимальная длина слова для расстановки переносов
        :param sep: символ переноса
        :return: str:
    """
    rus_worlds = regex.findall(r'\b[а-яА-Я]+\b', text)       # ищем все русскоязычные слова в тексте
    rus_worlds = list(set(rus_worlds))                              # убираем повторяющиеся слова
    for word in rus_worlds:
        if len(word) >= min_len_word_hyphenation:
            text = text.replace(word, hyphenation_in_word(word, sep))
    return text


def process_slug_fields(form: forms.ModelForm, field_4_sz_slug: str, field_4_js_old_slugs: str,
                        field_4_slug_make_from: str, model: models):
    """
    Функция обработки полей управляющих URL-слагами (для всех моделей cо слагами)
    :param form:                    -- форма модели
    :param field_4_sz_slug:         -- имя поля URL-слага
    :param field_4_js_old_slugs:    -- имя поля для хранения старых URL-слагов
    :param field_4_slug_make_from:  -- имя поля, из которого будем делать URL-слаг
    :param model:                   -- модель
    :return: None                   -- ничего не возвращает, т.к. изменяет данные непосредственно в form, а словари,
                                       а form.cleaned_data -- словарь, передаются по ссылке, а не по значению
    """
    # Получаем данные из формы (поля формы)
    form_data: dict = form.cleaned_data
    if form.instance.pk is None or form_data[field_4_js_old_slugs] is None:
        # если это новая запись или старых URL-слагов нет -- создадим список
        form_data[field_4_js_old_slugs] = []
    if form_data[field_4_sz_slug] is None or re.sub(r"\s+", "", form_data[field_4_sz_slug]) == "":
        # если в форме не указали URL-слаг, то создадим его из переменной make_slug_from
        created_slug = pytils.translit.slugify(form_data[field_4_slug_make_from]).lower()
        # создаём словарь для фильтрации проверки уникальности URL-слага
        filter_dict = {field_4_sz_slug: created_slug[:SLUG_LENGTH]}
        # проверим уникальность созданного URL-слага
        while model.objects.filter(**filter_dict).count() != 0:
            f"{created_slug[:SLUG_LENGTH-3]}-{int(random.uniform(0, 255)):x}"
        form_data[field_4_sz_slug] = created_slug
    if form.instance.pk is not None and form_data[field_4_sz_slug] != getattr(model.objects.get(id=form.instance.pk),
                                                                              field_4_sz_slug):
        # если это редактирование существующей записи и URL-слаг изменился, то добавим его в старые URL-слаги
        if getattr(model.objects.get(id=form.instance.pk), field_4_sz_slug) not in form_data[field_4_js_old_slugs]:
            form_data[field_4_js_old_slugs].append(getattr(model.objects.get(id=form.instance.pk), field_4_sz_slug))
        # если новый URL-слаг уже есть в старых URL-слагах, то удалим его из старых URL-слагов
        if form_data[field_4_sz_slug] in form_data[field_4_js_old_slugs]:
            form_data[field_4_js_old_slugs].remove(form_data[field_4_sz_slug])


def process_typograf_fields(form: forms.ModelForm, fields_4_typograf: list):
    """
    Функция обработки полей типографа (для всех моделей c типографом)
    СПРАВКА: hang_punct (Висячая пунктуация): '0' - Выключена;
                                              '1' - C помощью встроенного CSS;
                                              '2' - 'C помощью Class'.

             hyp (Переносы):                  '0' - Выключены;
                                              или число (в виде строки) длина слов, которых расставляем;
                                              '-1' - Очистить от переносов

             mnemo (Спец.символы):            '1' - Мнемокод;
                                              '2' - Юникод;
                                              '4' - Сделать <p> и <br> из CR и CRLF ('\n' и '\n\r');
                                              '5' - Очистить от HTML и мнемокода.

    :param form:                -- форма модели
    :param fields_4_typograf:   -- список полей, которые надо обработать типографом
    :return: None               -- ничего не возвращает, т.к. изменяет данные непосредственно в form, а словари,
                                   а form.cleaned_data -- словарь, передаются по ссылке, а не по значению
    """
    # Получаем данные из формы (поля формы)
    form_data: dict = form.cleaned_data
    sep = ''
    for field in fields_4_typograf:
        print(form_data[field], ' -> ')
        # ОБРАБОТКА МЕНЕМОКОДА И HTML
        if form_data['mnemo'] == '2':
            # очистить от HTML и странного мнемокода
            form_data[field] = html.unescape(form_data[field])
            sep = '­'
            print('-> ', form_data[field])
        if form_data['mnemo'] == '1':
            # очистить от HTML и странного мнемокода
            # TODO: исправить. Заменяет на мнемокод весь HTML (типа &lt;p&gt;Hello World&lt;/p&gt;)
            form_data[field] = html.escape(form_data[field])
            sep = '&shy;'
            print('-> ', form_data[field])
        # ОБРАБОТКА ПЕРЕНОСОВ
        if form_data['hyp'] == '-1':
            # Удаление переносов
            form_data[field] = form_data[field].replace('­', '').replace('&shy;', ' ')
            print('-> ', form_data[field])
        elif form_data['hyp'] != '0':
            # Расстановка переносов
            form_data[field] = hyphenation_in_text(form_data[field], int(form_data['hyp']), sep)
            print('-> ', form_data[field])
        # form_data[field] = html.unescape(form_data[field])
        # form_data[field] = safe_html_special_symbols(form_data[field])
        # form_data[field] = hyphenation_in_text(form_data[field])
        # form_data[field] = pytils.translit.detranslify(form_data[field])
        # form_data