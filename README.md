# yatube_project
Социальная сеть блогеров
### Описание
Благодаря этому проекту можно будет делиться своими мыслями и идеями.
Доступны: регистрация пользователей, публикация постов (в том числе и с изображениями), подписка на избранных авторов, возможность комментировать посты.
### Технологии
* Python 3.8
* Django 2.2.16
* *Также используются пакеты:*
mixer 7.1.2; 
Pillow 8.3.1; 
pytest 6.2.4; 
pytest-django 4.4.0; 
pytest-pythonpath 0.7.3; 
requests 2.26.0; 
six 1.16.0; 
sorl-thumbnail 12.7.0 .
### Запуск проекта в dev-режиме 
- Установите и активируйте виртуальное окружение (пример указан для Windows тут и ниже)
```
python -m venv venv
source venv/Scripts/activate

```
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
``` 
- В папке с файлом manage.py выполните команды:
```
python manage.py migrate
python manage.py runserver
```
- В проекте есть тесты, для запуска в папке с файлом manage.py выполните команду:
```
py manage.py test
```

### Авторы
Остапчук Дмитрий
