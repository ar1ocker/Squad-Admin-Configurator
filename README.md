# Squad Admin Configurator

Простая система управления администраторами и привилегированными пользователями для игры Squad

Помогает управлять наборами администраторов на ваших серверах Squad, выдавая каждому администратору отдельные роли на каждом сервере.

Есть возможность настроить дату окончания либо всех полномочий конкретного администратора, либо отдельно полномочий конкретного администратора на отдельном сервере

Конфигурацию админов можно использовать 2 путями:
- Через периодически обновляемые файлы на сервере
- Через получение файла по API

Администраторов добавлять через настраиваемые вебхуки, с возможностью проверки запроса по [HMAC](https://ru.wikipedia.org/wiki/HMAC)

![изображение](https://github.com/ar1ocker/Squad-Admin-Configurator/assets/109543340/325e8e9e-7139-477f-a7d3-c2cb8629aa09)

## Основные понятия относительно Squad Admin Configurator

- Сервер Squad - игровой сервер Squad или группа серверов с набором администраторов
- Администратор/Привилегированный - отдельный пользователь со своим набором ролей на каждом сервере Squad
- Роль - именованный набор игровых разрешений Squad
- Разрешение - [разрешение на сервере Squad](https://squad.fandom.com/wiki/Server_Administration)

## Запуск и настройка

- Клонируем репозиторий любым удобный способом
- Заполняем файл **infrastructure/.env** по примеру из **infrastructure/.env**
- Заполняем файл **squad-admin-configurator/config.toml** по примеру из **squad-admin-configurator/config.example.toml**

### Docker и Docker Compose

Проверено на версии 24.0, но вполне должно работать на 19+

Из папки **infrastructure/**

- Поднимаем 3 контейнера: Postgresql, Nginx и Squad-Admin-Configurator. Также будут автоматически выполнены миграции. Сервис будет доступен по адресу **<ваш ip>:1002/admin/**
```
# docker compose up -d
```

- Создаём административный аккаунт на сайте
```
# docker exec -it infrastructure-squad-admin-configurator-1 python3 manage.py createsuperuser
```

- При необходимости - импортируем уже существующий файл Admins.cfg с нашего сервера Squad
```
# docker cp ./Admins.cfg infrastructure-squad-admin-configurator-1:/
# docker exec -it infrastructure-squad-admin-configurator-1 python3 manage.py load_admin_config /Admins.cfg
```

- По дефолту для локальных конфигураций админов Squad создается каталог **~/squad_admin_configs/**

### Ручной запуск

Из папки **squad-admin-configurator/**

- Подготавливаем окружение
```
$ python3 -m venv venv
$ . venv/bin/activate
```

- Ставим зависимости
```
$ pip3 install -r requirements.txt
```

- Подготавливаем БД
```
$ python3 manage.py makemigrations
$ python3 manage.py migrate
$ python3 manage.py collectstatic
```

- Запускаем прослушивание порта
``` 
$ gunicorn "squad_admin_configurator.wsgi:application" --bind <требуемый ip или 0>:<ваш порт>
```

Ставим на cron команду, которая будет отслеживать истекшие привилегии

```
*/5 * * * * <путь до venv>/bin/python3 <путь до squad-admin-configurator>manage.py runcrons 
```

Либо же отдельным процессом запускаем:

- С активированным venv (`. venv/bin/activate`)
```
python3 manage.py cronloop -s 300 
```

- Без активированного venv
```
<путь до venv>/bin/python3 <путь до squad-admin-configurator>manage.py cronloop -s 300
```

Статика будет собрана в папку **squad-admin-configurator/static/**, её раздача при ручном запуске - на вашей совести, при запуске через Docker - статику раздаст Nginx
