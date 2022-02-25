# YaTube - blogging platform

Платформа для блогов, которая позволяет:

- Создавать и редактировать посты
- Читать посты других авторов и сообществ
- Оставлять лайки и комментарии
- Подписываться на авторов

http://yanktr.pythonanywhere.com/

### Технологии

Python 3.7, Django 2.2.19, SQLite, Bootstrap, HTML5 UP.

### Запуск проекта в dev-режиме

Клонировать репозиторий и перейти в него в командной строке:

```
> git clone https://github.com/yankovskaya-ktr/Yatube.git
> cd Yatube
```

Cоздать и активировать виртуальное окружение:

```
> python3 -m venv env
> source env/bin/activate
```

Установить зависимости из requirements.txt:

```
> python3 -m pip install --upgrade pip
> pip install -r requirements.txt
```

Выполнить миграции:

```
> python3 manage.py migrate
```

Запустить проект:

```
> python3 manage.py runserver
```
