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
    path('admin/', admin.site.urls),

    re_path(r'^$', views.index),
    # универсальный обработчик
    # re_path(r'^(?P<urn_block>[^/]*)/*$', views.index),
    # re_path(r'^(?P<urn_block>[^/]*)/*(?P<urn_roll>[^/]*)/*$', views.index),
]

# handler404 = 'web.views.handler404'
# handler500 = 'web.views.handler500'

if DEBUG:
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
