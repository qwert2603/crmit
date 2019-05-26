# Развертывание на хостинге

## Создание виртуального окружения

Перед началом развертывания нужно создать виртуальное окружение Python.

Виртуальное окружение находится в папке `crm.cmit22.ru/cgi/venv`, и, если эта папка существует, то повторно создавать виртуальное окружение не нужно.

Если папки `venv` нет, то открываем в терминале папку `crm.cmit22.ru/cgi` и создаем виртуальное окружение с помощью следующей команды:

```
virtualenv -p python3 venv
```

## Развертывание сайта

Переходим в папку `crm.cmit22.ru` и создаем в ней папку `deploy`, если она не была создана ранее.

В папке `deploy` создаем 3 файла, если они не были созданы ранее:
- [`apply_keys.py`](https://github.com/qwert2603/crmit/blob/master/deploy/apply_keys.py)
- [`deploy.sh`](https://github.com/qwert2603/crmit/blob/master/deploy/deploy.sh)
- [`keys.txt`](https://github.com/qwert2603/crmit/blob/master/deploy/keys.txt)

В файле `keys.txt` указываются секретные ключи, с помощью которых производится авторизация на сайте и в мобильном приложении. Эти ключи должны храниться в секрете. При изменении ключей всем пользователям потребуется повторно авторизоваться на сайте и в мобильном приложении.

Также в файле `keys.txt` указывается пароль БД.

При создании файла `keys.txt` нужно указать в нем секретные ключи и пароль БД.

Открываем в терминале папку `crm.cmit22.ru/deploy`.

Устанавливаем права на выполнение файла `deploy.sh`:

```
chmod 755 deploy.sh
```

Выполняем скрипт развертывания:

```
./deploy.sh x.y.z
```

`x.y.z` нужно заменить на номер последней версии из раздела [`releases`](https://github.com/qwert2603/crmit/releases).

В процессе развертывания выполняется:
- удаление старой версии сайта на хостинге
- скачивание указанной версии сайта
- распаковка новой версии сайта
- настройка переадресации запросов в Flask-приложение
- подстановка ключей и пароля БД из файла `keys.txt` в [файл конфигурации](https://github.com/qwert2603/crmit/blob/master/config.py)
- установка зависимостей
- выполнение миграций БД

Если требуется изменить пароль БД или секретные ключи, то нужно указать новые пароль и секретные ключи в файле `keys.txt` и выполнить развертывание повторно.

## Начало работы

Этот раздел описывает как добавить в систему первых руководителя, преподавателя, ученика, разработчика и бота, чтобы начать работать с сайтом.

Открываем в терминале папку `crm.cmit22.ru/cgi`.

Указываем Flask-приложение:

```
export FLASK_APP=start_dev.py
```

Запускаем python в контексте Flask-приложения:

```
venv/bin/python3 venv/bin/flask shell
```

В запущенном интерпретаторе python создаем руководителя, преподавателя, ученика, разработчика и бота:

```
from app.init_model import create_stub_models
create_stub_models()
```

Чтобы выйти из интерпретатора нужно нажать Ctrl+Z.

# Системные роли

Кроме системных ролей руководителя, преподавателя и ученика в CRM ЦМИТ также есть роли разработчика и бота.

## Системная роль "разработчик"

Эта роль предназначена для контроля за корректностью работы системы.

Разработчик имеет те же права в системе, что и руководитель.

Разработчик не может отправлять или получать сообщения. Также разработчик не может отправлять уведомления.

Разработчик может просматривать списки разработчиков и ботов, а также создавать новых разработчиков и ботов.

Разработчику доступны страницы сайта, позволяющие проверить целостность базы данных. Не все ограничения принятые в системе могут быть описаны средствами БД. К ним относятся:

- проверка того, что месяц платежа не выходит за рамки нахождения ученика в группе
- проверка того, что ученик посещает занятия в только тех группах, в которых состоит
- проверка того, что занятие не выходит за рамки функционирования группы
- проверка того, что каждая сущность "Преподаватель" ссылается на сущность "Системный пользователь" с ролью "преподаватель"

Страницы сайта, отвечающие за проверку целостности базы данных, позволяют проверить целостность этих и многих других ограничений в автоматическом режиме.

Все дополнительные страницы сайта, доступные разработчику, находятся в разделе ["еще"](http://crm.cmit22.ru/anth)

В целях предосторожности для разработчика можно включить режим READ_ONLY, при котором действия разработчика не будут сохраняться в системе. При включении этого режима после каждого запроса от разработчика будет выполняться команда `db.session.rollback()`, отменяющая все изменения в БД, сделанные во время обработки запроса. Исключение составляют запросы, отвечающие за авторизацию в системе, смену пароля и выход из системы.

Для включения режима READ_ONLY для разработчика нужно указать параметр `DEVELOPER_READ_ONLY = True` в файле конфигурации [config.py](https://github.com/qwert2603/crmit/blob/master/config.py).

## Системная роль "бот"

Эта роль предназначена для выполнения автоматических операций. Например, создание дампа.

Бот не может авторизовываться на сайте или в мобильном приложении.

Бот имеет доступ только к тем страницам на сайте, которые отмечены декоратором `@check_bot_access_token_with_logins`.
В параметре этого декоратора указывается список логинов ботов, которые имеют доступ к указанной странице.

По задумке, в системе присутствует только 1 бот с логином `dump_creator`, который делает дампы по расписанию.
Соответственно, есть только 1 метод с декоратором `@check_bot_access_token_with_logins`.
Это метод `dump` в [REST-API](https://github.com/qwert2603/crmit/blob/master/app/api_1_1_0/rests.py#L364).

# Создание дампа

Дамп создается с помощью скрипта [make_crmit_dump.py](https://github.com/qwert2603/crmit/blob/master/make_crmit_dump.py).

Необходимые параметры для создания дампа находятся в файле
[credentials.txt](https://github.com/qwert2603/crmit/blob/master/credentials.txt).

Список email получателей дампа указывается в переменной `mail_receivers` в скрипте `make_crmit_dump.py`.

Для получения `access_token` бота нужно выполнить REST-запрос авторизации, указав правильный пароль бота:

```
POST http://crm.cmit22.ru/api/v1.1.0/login
{
  "login": "dump_creator",
  "password": "the_password_of_bot",
  "device": "pc",
  "appVersion": "-1/12"
}
```

Для автоматического создания дапма по расписанию нужно настроить cron:
```
0 * * * * python3 /path/to/dir/make_crmit_dump.py
```

В приведенной команде нужно указать полный корректный путь к скрипту.