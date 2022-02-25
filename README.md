# Проект YaTube

YaTube — платформа для блогов, которая позволяет:

- создавать и редактировать посты
- читать посты других авторов и сообществ
- оставлять лайки и комментарии
- подписываться на авторов

http://yanktr.pythonanywhere.com/

### Технологии:

Python 3.7, Django 2.2.19, SQLite, Bootstrap, HTML5 UP.

### Локальный запуск проекта:

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
