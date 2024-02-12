# **⭐ Пригодилось? Звездочку поставь. ⭐**

# Squad Admin Configurator

Система управления привилегированными пользователями и ротациями карт для Squad

Помогает управлять наборами администраторов на ваших серверах Squad, выдавая каждому администратору отдельные роли на каждом сервере.
Есть возможность настроить дату окончания всех полномочий конкретного администратора, либо отдельно полномочий конкретного администратора на конкретном сервере

Конфигурацию админов можно использовать 2 путями:
- Через периодически обновляемые файлы на сервере
- Через получение файла по API

Привилегированных пользователей можно добавлять 3 путями:
- Напрямую через административную панель Django
- Через настраиваемые вебхуки, с возможностью проверки запроса по [HMAC](https://ru.wikipedia.org/wiki/HMAC) (в пару кликов можно связать с Battlemetrics или любыми кастомными ботами Discord, Telegram)
- Через REST api. Токен для доступа к API выдаётся через админку, имеется возможность ограничить токен в правах стандартными средствами Django (через установку пользователю прав доступа в админ панели)

Управление ротациями на ваших серверах, стандартно паки с картами заменяются раз в сутки, + есть возможность задать определенный пак на определенный день
Ротацию можно получать 2 путями:
- Через периодически обновляемые файлы на сервере
- Через получение файла по API

![изображение](https://github.com/ar1ocker/Squad-Admin-Configurator/assets/109543340/473af158-1851-42f5-b3ad-ee5e8fcbc905)

## Основные понятия относительно Squad Admin Configurator

- Сервер Squad - игровой сервер Squad или группа серверов с набором администраторов
- Администратор/Привилегированный - отдельный пользователь со своим набором ролей на каждом сервере Squad
- Роль - именованный набор игровых разрешений Squad
- Разрешение - [разрешение на сервере Squad](https://squad.fandom.com/wiki/Server_Administration)
- Ротация - набор паков с картами в определенном порядке
- Пак с картами - набор карт в определенном порядке

## Запуск и настройка

- Клонируем репозиторий любым удобный способом
- Заполняем файл **infrastructure/.env** по примеру из **infrastructure/.env**
- Заполняем файл **squad-admin-configurator/config.toml** по примеру из **squad-admin-configurator/config.example.toml**

### Docker и Docker Compose

Проверено на версии 24.0, но вполне должно работать на 19+

Из папки **infrastructure/**

- Поднимаем 3 контейнера: Postgresql, Nginx и Squad-Admin-Configurator. Также будут автоматически выполнены миграции. Сервис будет доступен по адресу **<ваш ip>:80/**
```
# docker compose up -d
```

- Создаём административный аккаунт на сайте
```
# docker exec -it infrastructure-squad-admin-configurator-1 python3 manage.py createsuperuser
```
Для некоторых старых версий Docker - названии контейнера может быть таким **infrastructure_squad-admin-configurator_1**

- При необходимости - импортируем уже существующий файл Admins.cfg с нашего сервера Squad
```
# docker cp <путь до Admins.cfg> infrastructure-squad-admin-configurator-1:/
# docker exec -it infrastructure-squad-admin-configurator-1 python3 manage.py load_admin_config /Admins.cfg
```

- По дефолту для локальных конфигураций админов Squad создается каталог **~/squad_admin_configs/** в хостовой системе

- При необходимости - импортируем уже существующие паки с нашего сервера Squad
```
# docker cp <путь до папки с паками> infrastructure-squad-admin-configurator-1:/
# docker exec -it infrastructure-squad-admin-configurator-1 sh
# python3 manage.py load_layer_pack /<папка с паками>/<пак>
```

- По дефолту для локальных ротаций Squad создается каталог **~/squad_rotations_configs/** в хостовой системе

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

# TODO

- Тесты
- (завершено 09.02.2024) API для получения списка привилегированных пользователей
- (завершено 09.02.2024) API для получения списка ролей у пользователя
- Ограничение персонала по добавлению определенных ролей на сервер 
