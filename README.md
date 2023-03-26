<h1 align="center">Проект социальной сети YaTube</h1>

Проект социальной сети, с возможностью публикации постов, подпиской на группы и авторов, а также комментированием постов. Также реализована возможность регистрации и авторизации пользователей.
### Стек технологий:
![python version](https://img.shields.io/badge/Python-3.7.9-green)
![django version](https://img.shields.io/badge/Django-2.2.16-green)
![Html](https://img.shields.io/badge/HTML-green)
![CSS](https://img.shields.io/badge/CSS-green)
![Bootstrap](https://img.shields.io/badge/Bootstrap-green)
### Запуск проекта в dev-режиме:
1. Склонировать репозиторий:
```
git clone https://github.com/Artem-Bespalov/hw05_final
```
2. Установить и активировать виртуальное окружение:
```
python -m venv venv
```
```
source venv/Scripts/activate
```
3. Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
4. Выполнить миграции:
```
python manage.py migrate
```
5. Запустить сервер:
```
python manage.py runserver
```
### Примеры запросов:

* ```posts/{id}``` - Получение, изменение или удаление поста(GET, PUT, PATCH, DELETE)
* ```posts/{post_id}/comments/``` - Получение комментариев к посту(GET)
* ```posts/{post_id}/comments/{id}``` - Получение, изменение или удаление комментария(GET, PUT, PATCH, DELETE)
* ```group/{slug:slug}``` - Подробная информация о группе(GET)
* ```profile/{usermane}/``` - Профайл пользователя(GET)
* ```follow/``` - Получение избранных авторов(GET)

### Автор:
<a href="https://github.com/Artem-Bespalov">Артем Беспалов</a>
