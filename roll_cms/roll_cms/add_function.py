# -*- coding: utf-8 -*-
# ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ ПРОЕКТА ROLL_CMS (не вьшки)

from roll_cms.settings import *
from django.http import HttpRequest, HttpResponse
import regex


def check_cookies(request: HttpRequest) -> bool:
    # проверка, что посетитель согласился со сбором данных через cookies
    if request.COOKIES.get('cookie_accept'):
        return False
    return True


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


def hyphenation_in_word(s: str) -> str:
    """ Расстановка переносов в слове
    рецепт: https://ru.stackoverflow.com/questions/900660/Расстановка-переносов-в-русских-словах

    :param s:     Слово в котором надо расставить переносы
    :return: str: Слово с расставленными переносами
    """
    # расстановка переносов в слове
    def is_vow(let: str) -> bool:
        return let.upper() in ['А', 'О', 'И', 'Е', 'Ё', 'Э', 'Ы', 'У', 'Ю', 'Я']

    def is_cons(let: str) -> bool:
        return let.upper() in ['Б', 'В', 'Г', 'Д', 'Ж', 'З', 'К', 'Л', 'М', 'Н', 'П', 'Р', 'С', 'Т', 'Ф', 'Х', 'Ц',
                               'Ч', 'Ш', 'Щ']

    def vow_inds(wrd: str):
        return [i for i in range(len(wrd) - 2) if is_vow(wrd[i])]

    word = s
    vow_indices = vow_inds(word)
    if vow_indices and vow_indices[0] + 2 < len(word):
        for ind in vow_indices:
            sep = '­'
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
    print(f'Варианты расстановки переносов слова "{s}" - [ {word} ]')
    return word


def hyphenation_in_text(text: str, min_len_word_hyphenation: int = 14) -> str:
    """ Расстановка переносов в тексте

        :param text:   строка которую надо очистить
        :param min_len_word_hyphenation: минимальная длина слова для расстановки переносов
        :return: str:
    """
    rus_worlds = regex.findall(r'\b[а-яА-Я]+\b', text)          # ищем все русскоязычные слова в тексте
    rus_worlds = list(set(rus_worlds))                              # убираем повторяющиеся слова
    for word in rus_worlds:
        if len(word) >= min_len_word_hyphenation:
            text = text.replace(word, hyphenation_in_word(word))
    return text
