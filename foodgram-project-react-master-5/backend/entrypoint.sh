#!/bin/bash
set -x

# Искусственное ожидание БД
sleep 10

python manage.py makemigrations

python manage.py migrate

echo "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(username='skrynch33').exists())" | python manage.py shell | grep "True" || (

  echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('skrynch33', 'dubkibobri@mail.ru', '199021ppc1313Aa')" | python manage.py shell
)

echo "from recipes.models import Ingredient; print(Ingredient.objects.exists())" | python manage.py shell | grep "True" || (

  python manage.py upload_json_to_db /app/data/ingredients.json
)

python manage.py collectstatic --noinput
