# Foodgram

foodgram - это сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

status badge - [![Main foodgram workflow](https://github.com/Skrynch/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/Skrynch/foodgram-project-react/actions/workflows/main.yml)

Стек-технологий

- Django REST
- Python 3.9
- Gunicorn
- Nginx
- JS
- Node.js
- PostgreSQL
- Docker

Установка и развертвывание проекта

Примечание: Все примеры указаны для Linux

### Склонируйте репозиторий на свой компьютер:

git clone git@github.com:Skrynch/foodgram-project-react.git
Создайте файл .env и заполните его своими данными. Все необходимые переменные перечислены в файле .env.example, находящемся в 
корневой директории проекта.
Создание Docker-образов

### Замените YOUR_USERNAME на свой логин на DockerHub:

cd frontend
docker buildx build --platform=linux/amd64 -t skrynch/foodgram_frontend .
cd ../backend
docker buildx build --platform=linux/amd64 -t skrynch/foodgram_backend .
cd ../infra
docker buildx build --platform=linux/amd64 -t skrynch/foodgram_gateway . 

### Загрузите образы на DockerHub:

docker push skrynch/foodgram_frontend
docker push skrynch/foodgram_backend
docker push skrynch/foodgram_gateway

### Деплой на сервере:

Подключитесь к удаленному серверу

ssh -i PATH_TO_SSH_KEY/SSH_KEY_NAME YOUR_USERNAME@SERVER_IP_ADDRESS 

### Создайте на сервере директорию foodgram:

mkdir foodgram

### Установите Docker Compose на сервер:

sudo apt update
sudo apt install curl
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose

### Скопируйте файлы docker-compose.production.yml и .env в директорию foodgram/ на сервере:

scp -i PATH_TO_SSH_KEY/SSH_KEY_NAME docker-compose.production.yml 
YOUR_USERNAME@SERVER_IP_ADDRESS:/home/YOUR_USERNAME/foodgram/docker-compose.production.yml
Где:

PATH_TO_SSH_KEY - путь к файлу с вашим SSH-ключом
SSH_KEY_NAME - имя файла с вашим SSH-ключом
YOUR_USERNAME - ваше имя пользователя на сервере
SERVER_IP_ADDRESS - IP-адрес вашего сервера
Запустите Docker Compose в режиме демона:

Выполните миграции, соберите статические файлы бэкенда и скопируйте их в /backend_static/static/:

sudo docker-compose -f /home/yc-user/foodgram/docker-compose.production.yml exec backend python manage.py migrate
sudo docker-compose -f /home/yc-user/foodgram/docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker-compose -f /home/yc-user/foodgram/docker-compose.production.yml exec backend cp -r /app/collected_static/. 
/backend_static/static/

### Откройте конфигурационный файл Nginx в редакторе nano:

sudo nano /etc/nginx/sites-enabled/default

### Измените настройки location в секции server:

location / {
    proxy_set_header Host $http_host;
    proxy_pass http://127.0.0.1:8800;
}

### Проверьте правильность конфигурации Nginx:

sudo nginx -t

### Если вы получаете следующий ответ, значит, ошибок нет:

nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful

### Перезапустите Nginx:

sudo service nginx reload
Настройка CI/CD

### Файл workflow уже написан и находится в директории:

foodgram/.github/workflows/main.yml
Для адаптации его к вашему серверу добавьте секреты в GitHub Actions:

DOCKER_USERNAME                # имя пользователя в DockerHub
DOCKER_PASSWORD                # пароль пользователя в DockerHub
HOST                           # IP-адрес сервера
USER                           # имя пользователя
SSH_KEY                        # содержимое приватного SSH-ключа (cat ~/.ssh/id_rsa)
SSH_PASSPHRASE                 # пароль для SSH-ключа

TELEGRAM_TO                    # ID вашего телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
TELEGRAM_TOKEN                 # токен вашего бота (получить токен можно у @BotFather, команда /token, имя бота)

### Команда для загрузки ингредиентов из JSON файла:

Эта команда позволяет загрузить список ингредиентов из файла JSON в базу данных.

Использование
Убедитесь, что ваш JSON файл соответствует требуемому формату, где каждый ингредиент должен содержать поля name и measurement_unit.

Выполните команду, указав путь к файлу JSON:

````
python manage.py <имя_команды> путь/к/файлу.json
````

Замените <имя_команды> на фактическое имя вашей команды в приложении.

Пример файла JSON
````
[
    {
        "name": "Томат",
        "measurement_unit": "шт"
    },
    {
        "name": "Мука",
        "measurement_unit": "гр"
    }
    // Другие ингредиенты...
]
````


Автор проекта - Зотов Илья, студент 27 кагорты python +


