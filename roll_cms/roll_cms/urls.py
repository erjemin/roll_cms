# -*- coding: utf-8 -*-
"""
Конфигурация URL для проекта roll_cms.

Список `urlpatterns` направляет URL-адреса в представления (вьюшки). Дополнительную информацию см.:
     https://docs.djangoproject.com/en/4.2/topics/http/urls/
Примеры:
Представления функций
     1. Добавьте импорт: from my_app import views
     2. Добавьте URL-адрес в urlpatterns: path('', views.home, name='home')
Представления на основе классов
     1. Добавьте импорт: from other_app.views import Home
     2. Добавьте URL-адрес в шаблоны URL-адресов: path('', Home.as_view(), name='home')
Включение другой конфигурации URL
     1. Импортируйте функцию include(): from django.urls import include, path
     2. Добавьте URL-адрес в urlpatterns: path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import include
from django.conf.urls.static import static
from roll_cms.settings import *
from roll_cms import views


urlpatterns = [
    # для работы django-filer
    re_path(r'^filer/', include('filer.urls')),
    # re_path(r'^file_t/', include('filer.urls')),

    # # для работы ckeditor_filebrowser_filer и ckeditor
    # path('ckeditor/', include('filer.urls')),
    # re_path(r'^filebrowser_filer/', include('ckeditor_filebrowser_filer.urls')),
    # # для починки ckeditor_filebrowser в соответствии с рецептом
    # # https://githubhelp.com/nephila/django-ckeditor-filebrowser-filer/issues/41
    # re_path(r'^filebrowser_filer/filer_', include('ckeditor_filebrowser_filer.urls')),

    # Админка по нестандартному адресу! По стандартному адресу установить ловушку для ботов на уровне nginx и fail2ban
    path('ad-min/', admin.site.urls),

    # Главная страница
    re_path(r'^$', views.index),
    # Универсальный обработчик URN
    re_path(rf'^(?P<urn_chain>({URL_PREFIX_ROLL}|{URL_PREFIX_ITEM})\d+-\S+)$', views.universal_processor),
    # в будущем будет универсальный обработчик с обработкой тегов
    # re_path(rf'^(?P<urn_chain>({URL_PREFIX_ROLL}|{URL_PREFIX_ITEM}|{URL_PREFIX_TAGG})\d+-[\s\S]+)$',
    #         views.universal_processor),
]

# handler404 = 'web.views.handler404'
# handler500 = 'web.views.handler500'

if DEBUG:
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
