# IOC

## Описание

Для создания гибких и расширяемых приложений хорошо подходит система плагинов. В такой системе плагины отвечают за создание и связывание друг с другом объектов приложения (например, различных реализаций сервисов или репозиториев). Для этого необходимо иметь хранилище всех объектов. С этой ролью отлично справляется паттерн [Service Locator](https://martinfowler.com/articles/injection.html#UsingAServiceLocator), а проект **{ioc}** является простой в использовании и легковесной его реализацией. 

Система плагинов вместе с **{ioc}** поможет, если необходимо:
* удобно включать/выключать части функционала приложения;
* устанавливать приложение нескольким клиентам, у некоторых из которых часть функционала должна быть индивидуальной;
* расширять приложение путем установки сторонних пакетов.

## Основные возможности

* В [стандартной реализации](https://martinfowler.com/articles/injection.html#ADynamicServiceLocator) паттерна Service Locator для каждого класса хранится его единственный экземпляр. В этой библиотеке вместо экземпляра хранится фабрика, позволяющая гибко управлять созданием объектов. 
* Для получения объектов одного и того же типа можно зарегистрировать несколько разных реализаций фабрик и выбирать между ними. 
* Присутствует возможность передачи параметров при вызове фабрики.
* Поддержка статического анализа кода. Благодаря этому IDE подсказывает названия и типы параметров, а также тип возвращаемого результата при вызове фабрик, что значительно упрощает написание кода и позволяет избегать глупых ошибок.
* Поддержка декораторов для фабрик, с помощью которых можно влиять на создание объектов. Например, для всех создаваемых объектов добавить логирование или для объектов некоторого типа добавить кеширование.

Стоит отметить, что Service Locator [является антипаттерном](https://blog.ploeh.dk/2010/02/03/ServiceLocatorisanAnti-Pattern/). К его недостаткам относится сокрытие зависимостей. В примерах ниже приведен способ использования этой библиотеки, сводящий недостатки паттерна Service Locator к минимуму: Service Locator используется только в плагинах, но не в самих классах приложения. В классах приложения зависимости указываются явным образом в конструкторах. 

## Примеры использования

Чтобы продемонстрировать возможности библиотеки, представим следующий пример. Продуктовая IT-компания разрабатывает продукт, позволяющий их клиентам — другим компаниям — поздравлять своих сотрудников с днем рождения через мессенджер. Среди клиентов есть компании из разных стран, а список используемых мессенджеров включает WhatsApp, Telegram и внутренние корпоративные мессенджеры компаний.

### Система плагинов

Эта библиотека хорошо работает с какой-либо системой плагинов, в которой плагины позволяют создавать и связывать объекты приложения (сервисы, репозитории) друг с другом. Данная библиотека не предоставляет реализацию системы плагинов, т.к. это не является её ответственностью. Чтобы использовать данную библиотеку, придется взять готовую реализацию системы плагинов или реализовать ее самому. Для данных примеров реализуем систему плагинов самостоятельно.

Эта реализация системы плагинов будет очень проста, но в то же время достаточно функциональна, чтобы продемонстрировать все возможности библиотеки **ioc**. В этой системе плагинов в конфигурационном файле будут содержаться названия модулей. Каждый такой модуль будет содержать функцию `load`, которая будет отвечать за создание и регистрацию объектов приложения в Локаторе Служб. При запуске приложения эти модули будут импортированы, а затем для каждого из них будет вызвана функция `load`.

### Приложение для поздравления сотрудников

#### Структура проекта

Проект будет иметь следующую структуру:

```text
.
├── module_names.txt
├── setup.py
└── src
   └── congratulations_app
      ├── __init__.py
      ├── __main__.py
      ├── congratulations_services
      │  ├── __init__.py
      │  ├── english.py
      │  └── russian.py
      └── messengers
         ├── __init__.py
         ├── telegram.py
         └── whatsapp.py
```

#### Конфигурационный файл

Файл `module_names.txt` — это тот самый конфигурационный файл, в котором перечислены модули. Эти модули будут импортированы и у каждого будет вызвана функция `load`. Пример содержимого файла `module_names.txt`:

```
congratulations_app.messengers.telegram
congratulations_app.congratulations_services.russian
```

Как видно, в качестве мессенджера используется Telegram. Если будет необходимость заменить мессенджер Telegram на WhatsApp, например, при установке приложения другому клиенту с таким требованием, то достаточно будет заменить строчку `congratulations_app.messengers.telegram` на `congratulations_app.messengers.whatsapp` в конфигурационном файле нового клиента. Таким образом можно заменить любой объект приложения на любой другой без необходимости модификации кода.

#### Реализация мессенджеров

Файл `src/congratulations_app/messengers/__init__.py` содержит интерфейс мессенджера — `Messenger` и интерфейс фабрики мессенджера — `MessengerFactory`. Интерфейс фабрики необходим, чтобы задать контракт, который будут использовать другие модули для получения этого объекта.

```python
# src/congratulations_app/messengers/__init__.py

__all__ = [
    "Messenger",
    "MessengerFactory",
]


class Messenger:
    def send_message(self, name: str, message: str) -> None:
        raise NotImplementedError()


class MessengerFactory:
    def __call__(self) -> Messenger:
        raise NotImplementedError()
```

Рассмотрим одну из реализаций мессенджера — Telegram, которая содержится в модуле `src/congratulations_app/messengers/telegram.py`. Этот модуль содержит реализацию интерфейса `Messenger` — `TelegramMessenger` и функцию `load`. Эта функция будет вызвана при инициализации приложения, если этот модуль указан в конфигурационном файле `module_names.txt`. В ней создается экземпляр класса `TelegramMessenger` и фабрика, которая его возвращает, — `TelegramMessengerFactory`. Затем эта фабрика регистрируется в Локаторе Служб с помощью функции `add_factory` из библиотеки **ioc**. После чего с помощью этой фабрики можно будет получить экземпляр класса `Messenger` в другом модуле. Аналогичным образом реализован модуль `src/congratulations_app/messengers/whatsapp.py`

```python
# src/congratulations_app/messengers/telegram.py

from galo_ioc import add_factory
from congratulations_app.messengers import Messenger, MessengerFactory


__all__ = [
    "TelegramMessenger",
    "load",
]


class TelegramMessenger(Messenger):
    def send_message(self, name: str, message: str) -> None:
        print(f"Message {message!r} sent to {name!r} via Telegram.")


def load() -> None:
    class TelegramMessengerFactory(MessengerFactory):
        def __call__(self) -> Messenger:
            return messenger

    messenger = TelegramMessenger()
    add_factory(MessengerFactory, TelegramMessengerFactory())
```

#### Реализация сервисов поздравлений

Теперь перейдем к одной из реализаций сервиса поздравлений, которая содержится в модуле `src/congratulations_app/congratulation_services/russian.py`. Функция `load` в этом модуле отвечает за создание объекта типа `RussianCongratulationsService` и регистрацию его фабрики в Локаторе Служб. Для получения зависимости `messenger` используется функция `get_factory`. Она позволяет получить доступ к фабрике `MessengerFactory`, которая в данный момент зарегистрирована в Локаторе Служб. Это может быть `TelegramMessengerFactory`, `WhatsAppMessengerFactory` или любая другая. Затем экземпляр класса `Messenger` получается путем вызова этой фабрики. После чего он передается в конструктор класса `RussianCongratulationsService` для его создания.

```python
# src/congratulations_app/congratulation_services/russian.py

from galo_ioc import add_factory, get_factory
from congratulations_app.messengers import Messenger, MessengerFactory
from congratulations_app.congratulations_services import CongratulationsService, CongratulationsServiceFactory


__all__ = [
    "RussianCongratulationsService",
    "load",
]


class RussianCongratulationsService(CongratulationsService):
    def __init__(self, messenger: Messenger) -> None:
        self.__messenger = messenger

    def happy_birthday(self, name: str) -> None:
        self.__messenger.send_message(name, f"С днем рождения, {name}!")


def load() -> None:
    class RussianCongratulationsServiceFactory(CongratulationsServiceFactory):
        def __call__(self) -> CongratulationsService:
            return service

    messenger_factory = get_factory(MessengerFactory)
    messenger = messenger_factory()
    service = RussianCongratulationsService(messenger)
    add_factory(CongratulationsServiceFactory, RussianCongratulationsServiceFactory())
```

Благодаря использованию интерфейсов фабрик работает статический анализ кода и автодополнение.

__<Тут гифка>__

#### Реализация функции запуска приложения

В функции запуска приложения происходит чтение конфигурационного файла и загрузка модулей. Функция `get_factory` (аналогично с`set_factory`) обращается к контейнеру фабрик в текущем контексте. Чтобы добавить в текущий контекст контейнер фабрик, нужно использовать выражение `with FactoryContainerImpl():`.

```python
from galo_ioc import FactoryContainerImpl, get_factory
from congratulations_app.startup_utils import get_module_names_path, read_module_names, load_plugins
from congratulations_app.congratulations_services import CongratulationsServiceFactory


def main() -> None:
    module_names_path = get_module_names_path()
    module_names = read_module_names(module_names_path)
    with FactoryContainerImpl():
        load_plugins(module_names)
        congratulations_service_factory = get_factory(CongratulationsServiceFactory)
        congratulations_service = congratulations_service_factory()
        congratulations_service.happy_birthday("Maria")


if __name__ == "__main__":
    main()
```

При содержимом файла `module_names.txt`:

```text
congratulations_app.messengers.telegram
congratulations_app.congratulations_services.russian
```

Будет выведено:

```text
Message 'С днем рождения, Maria!' sent to 'Maria' via Telegram.
```

Но если изменить содержимое файла `module_names.txt` на:

```text
congratulations_app.messengers.whatsapp
congratulations_app.congratulations_services.english
```

Получим вывод:

```text
Message 'Happy birthday, Maria!' sent to 'Maria' via WhatsApp.
```

### Реализация сторонних плагинов

Теперь рассмотрим интеграцию в приложение сторонних плагинов. Например, новый заказчик хочет использовать приложение для поздравлений сотрудников с днем рождения, но он не хочет использовать ни один из уже реализованных мессенджеров, а вместо них хочет использовать свой внутренний корпоративный мессенджер. В месте с тем этот заказчик против включения реализации своего корпоративного мессенджера в кодовую базу приложения. Даже этот случай не является проблемой для библиотеки **ioc** совместно с системой плагинов. Для решения данной задачи необходимо создать отдельный проект. 

#### Структура проекта

Структура проекта будет выглядеть следующим образом:

```text
.
├── setup.py
└── src
   └── secret_corporation_plugin
      ├── __init__.py
      └── messengers
         ├── __init__.py
         └── secret_corporation.py
```

#### Реализация внутреннего корпоративного мессенджера

Рассмотрим реализацию модуля `src/secret_corporation_plugin/messengers/secret_corporation.py`. Как можно видеть, она ничем принципиально не отличается от реализации двух других мессенджеров: `Telegram` и `WhatsApp`, включенных в кодовую базу приложения.

```python
# src/secret_corporation_plugin/messengers/secret_corporation.py

from galo_ioc import add_factory
from congratulations_app.messengers import Messenger, MessengerFactory


__all__ = [
    "SecretCorporationMessenger",
    "load",
]


class SecretCorporationMessenger(Messenger):
    def send_message(self, name: str, message: str) -> None:
        print(f"Message {message!r} sent to {name!r} via Secret Corporation Messenger.")


def load() -> None:
    class SecretCorporationMessengerFactory(MessengerFactory):
        def __call__(self) -> Messenger:
            return messenger

    messenger = SecretCorporationMessenger()
    add_factory(MessengerFactory, SecretCorporationMessengerFactory())
```

#### Интеграция стороннего плагина в приложение

Чтобы использовать реализацию внутреннего корпоративного мессенджера в приложении вместо `Telegram` или `WhatsApp`, необходимо установить пакет `secret_corporation_plugin` с помощью команды `python setup.py install .` в корневой директории проекта с этим мессенджером. Далее в конфигурационном файле `module_names.txt` в качестве модуля с мессенджером указать `secret_corporation_plugin.messengers.secret_corporation`. В результате содержимое файла `module_names.txt` может выглядеть следующим образом:

```text
secret_corporation_plugin.messengers.secret_corporation
congratulations_app.congratulations_services.russian
```

И при запуске приложения с таким содержимым файла `module_names.txt` получим следующий вывод:

```text
Message 'С днем рождения, Maria!' sent to 'Maria' via Secret Corporation Messenger.
```

Как можно видеть в качестве мессенджера используется `SecretCorporationMessenger`. Чтобы этого добиться, не потребовалось изменять код приложения, а достаточно было лишь добавить другую реализацию мессенджера в другом проекте и изменить конфигурационный файл.
