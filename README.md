# Foodgram
### Описание
Сайт Foodgram, «Продуктовый помощник». Онлайн-сервис и API для него. На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
### Технологии
Django Rest Framework
Python 3.7,
Django 2.2.16,
JWT,
Postgres 13.0
### Создание docker-compose и запуск проекта на сервере
 - 1) Клонировать репозиторий и перейти в него в командной строке
git clone git@github.com:evstigneefff/foodgram-project-react.git
 - 2) Отредактировать файл infra/docker-compose.yml,
 указав свои данные doker hub
- 3) Actions secrets and variables:
DB_ENGINE=django.db.backends.postgresql
DB_HOST=db
DB_NAME
DB_PORT=5431
DJANGO_SECRET_KEY
DOCKER_PASSWORD
DOCKER_USERNAME
HOST
PASSPHRASE
POSTGRES_DB
POSTGRES_PASSWORD
POSTGRES_USER
SSH_KEY
USER
 - 4) Скопиропать на сервер:
scp infra/docker-compose.yml
scp infra/nginx.conf
 - 5) Выполнить push в репозиторий github
 - 6) После успешного завершения workflow на github выполнить миграции, собрать статику,
      загрузить список ингридиентов, создать superuser:
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --no-input
docker-compose exec backend python manage.py get_ingr_from_json
docker-compose exec backend python manage.py createsuperuser

Проект будет доступен по адресу http://<ip_вашего_сервера>/
Админ панель django будет доступна по адресу http://<ip_вашего_сервера>/admin/
Документация api будет доступна по адресу http://<ip_вашего_сервера>/docs/redoc.html
Api будет доступен по адресу http://<ip_вашего_сервера>/api/
### Автор
https://github.com/Evstigneefff