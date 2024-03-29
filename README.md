# Foodgram
### О проекте
Foodgram - это агрегатор рецептов или продуктовый помощник. Пользователи могут регистрироваться и выкладывать свои собственные рецепты. Существует система фильтрации рецептов по тегам. У пользователей есть возможно добавлять рецепты в избранное, в список покупок, а так же подписываться на других пользователей. После добавления одного или нескольких рецептов в список покупок у пользователя есть возможность скачать его в виде текстового файла и распечатать.


### Технологии
В данном проекте я отвечал за бэкенд-часть и использовал следующие технологии:
- Python
- Django
- DRF
- Djoser
- Docker
- PostgreSQL
- nginx
- gunicorn

Фронтенд написан на React



### Как запустить проект
Проект запускается в контейнерах Docker:
- Скачать из репозитория на гитхабе файлы docker-compose.yml и nginx.conf из папки infra

- Загрузить эти файлы на сервер, где будет запущен проект

- В одной директории с файлами docker-compose.yml и nginx.conf создать .env-файл и наполнить его следущими данными:
```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=password # пароль для подключения к БД (установите свой)
DB_HOST=my_container # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
```
- Запустить контейнер:
```
docker-compose up
```
- Выполнить в контейнере backend следующие команды:
```
docker-compose exec backend python manage.py migrate
```
```
docker-compose exec backend python manage.py createsuperuser
```
```
docker-compose exec backend python manage.py collectstatic --no-input 
```

Проект будет доступен локально по адресу:

```
http://localhost/
```





