# IOC

Для того чтобы создать приложение, возможности которого можно расширять путем установки сторонних пакетов, может потребоваться система плагинов. В такой системе плагины отвечают за создание и связывание друг с другом компонентов приложения. Для решения этой задачи необходимо иметь хранилище для всех компонентов. С этой ролью отлично справляется паттерн Service Locator, а проект ioc является простой в использовании и легковесной его реализацией. Система плагинов также может потребоваться в случае, когда приложение устанавливается нескольким клиентам, у каждого из которых должен быть свой набор компонентов.

## Описание

Данная библиотека представляет собой реализацию паттерна [Service Locator](https://martinfowler.com/articles/injection.html#UsingAServiceLocator). Во многих реализациях этого паттерна для каждого класса хранится его единственный экземпляр. В этой библиотеке вместо экземпляра хранится фабрика, позволяющая гибко управлять созданием объектов. При необходимости для одной и той же зависимости можно зарегистрировать несколько фабрик и выбирать между ними при разрешении этой зависимости. К тому же присутствует возможность передачи параметров при вызове фабрики.

К плюсам библиотеки также относится поддержка декораторов для фабрик. Это позволяет влиять на создание и разрешение зависимостей. С их помощью можно добавить новые возможности для создаваемых объектов. Например, добавить кеширование или логирование. **(TODO: добавить ещё примеров)**

Большим преимуществом является поддержка статического анализа кода. Благодаря этому IDE подсказывает названия и типы параметров, а также при вызове фабрики известен тип возвращаемого результата, что упрощает написание кода и позволяет избегать глупых ошибок.

Известно, что Service Locator является антипаттерном. К его недостаткам относится сокрытие зависимостей. В примерах использования этой библиотеки предложен способ использования, сводящий недостатки этого паттерна к минимуму. А именно Service Locator используется только в плагинах, но не в самих компонентах приложения. В компонентах приложения зависимости указываются явным образом в конструкторе.   

## Примеры использования

Чтобы продемонстрировать возможности библиотеки, представим следующий пример. Продуктовая IT компания разрабатывает продукт, позволяющий их клинентам - другим компаниям - поздравлять своих сотрудников с днем рождения через мессенджер для повышения командного духа **(TODO: Придумать причину получше)**. Среди их клиентов есть как российские, так и зарубежные компании, а список используемых мессенджеров включает Telegram, WhatsApp и внутренние корпоративные мессенджеры компаний.

### Система плагинов

Эта библиотека хорошо работает в связке с какой-либо системой плагинов, в которой плагины позволяют создавать и связывать компоненты приложения друг с другом. Данная библиотека не предоставляет реализацию системы плагинов, т.к. это не является её ответственностью. Чтобы использовать данную библиотеку, придется взять готовую реализацию системы плагинов **(дать ссылку на раздел где перечислены готовые системы плагинов)** или реализовать ее самому. Для данных примеров реализуем систему плагинов самостоятельно.

Эта реализация системы плагинов будет очень проста, но в тоже время достаточно функциональна, чтобы продемонстрировать все возможности библиотеки ioc **(потом поправить название)**. В этой системе плагинов в конфигурационном файле будут содержаться названия модулей. Каждый такой модуль будет содержать функцию `load`, которая будет отвечать за создание и регистрацию компонентов приложения в Локаторе Служб. При запуске приложения эти модули будут импортироваться и затем у них будет вызываться функция `load`. Что позволит создать и связать друг с другом необходимые компоненты приложения.

### Структура проекта

Наш проект будет иметь следующую структуру:

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

Файл `module_names.txt` это тот самый конфигурационный файл, в котором перечислены модули, которые будут импортированы, и у которых будет вызвана фукнкция `load`. Пример содержимого файла `module_names.txt`:

```
congratulations_app.messengers.telegram
congratulations_app.congratulations_services.russian
```

Как видно, в качестве мессенджера испльзуется Telegram. Если будет необходимость заменить мессенджер Telegram на WhatsApp, например, при установке приложения другому клиенту с таким запросом, то достаточно будет заменить строчку `congratulations_app.messengers.telegram` на `congratulations_app.messengers.whatsapp` в конфигурационном файле нового клиента. Таким образом можно заменить любой компонент Вашего приложения на любой другой без необходимости модификации кода.


Перейдем к реализации мессенджеров. В файле `src/congratulations_app/messengers/__init__.py` содержится интерфейс мессенджера - `Messenger` и интерфейс фабрики мессенджера - `MessengerFactory`. Интерфейс фабрики необходим, чтобы задать контракт, который будут использовать другие модули для получения этого компонента.

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

Рассмотрим одну из реализаций мессенджера - Telegram, которая содержится в модуле `src/congratulations_app/messengers/telegram.py`. Этот модуль содержит реализацию интерфейса `Messenger` - `TelegramMessenger` и фукнцию `load`. Фукнция `load` это как раз та самая функция, которая может быть вызвана при инициализации приложения, если этот модуль указан в конфигурационном файле `module_names.txt`. Функция `load` создает экземпляр класса `TelegramMessenger`, фабрику которая его возвращает и регистрирует эту фабрику в Локаторе Служб с помощью функции `add_factory` из библиотеки `ioc`. Затем эта фабрика может быть вызвнана в других модулях, чтобы получить экземпляр класса `Messenger`. Аналогичным образом реализован модуль `src/congratulations_app/messengers/whatsapp.py`

```python
# src/congratulations_app/messengers/telegram.py

from ioc.context import add_factory
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

Теперь перейдем к одной из реализаций сервиса поздравлений, которая содержится в модуле `src/congratulations_app/congratulation_services/russian.py`. Фукнция `load` в этом модуле отвечает за создание компонента `RussianCongratulationsService` и регистрацию его фабрики в Локаторе служб. Для получения зависимости `messenger` используется фукнция `get_factory`. Она позволяет получить доступ к фабрике `MessengerFactory`, которая в данный момент зарегистрирована в Локаторе Служб. Это может быть `TelegramMessengerFactory`, `WhatsAppMessengerFactory` или любая другая. Затем экземпляр класса `Messenger` получается путем вызова этой фабрики. После чего он передается в конструктор класса `RussianCongratulationsService` для его создания.

```python
# src/congratulations_app/congratulation_services/russian.py

from ioc.context import add_factory, get_factory
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

Благодаря использованию интерфейсов фабрик работает статический анализ кода и автодополнение в частности. 

__<Тут гифка>__


Теперь перейдем к реализации точки входа в приложение. В ней происходит чтение конфигурационного файла, загрузка модулей и затем работа приложения. Функции `get_factory` и `set_factory` обращаются к контейнеру фабрик в текущем контексте. Чтобы добавить в текущий контекст контейнер фабрик нужно использовать выражение `with factory_container():`. Затем в контексте этого контейнера можно вызывать фукнции `get_factory` и `set_factory`. 

```python
from typing import Sequence
from importlib import import_module
from ioc.context import get_factory
from ioc.factory_container_impl import FactoryContainerImpl
from congratulations_app.congratulations_services import CongratulationsServiceFactory


def main(module_names_path: str = "module_names.txt") -> None:
    module_names = read_module_names(module_names_path)
    with FactoryContainerImpl():
        load_plugins(module_names)
        congratulations_service_factory = get_factory(CongratulationsServiceFactory)
        congratulations_service = congratulations_service_factory()
        congratulations_service.happy_birthday("Maria")


def read_module_names(module_names_path: str) -> Sequence[str]:
    with open(module_names_path, mode="r") as file:
        return [name.strip() for name in file.readlines()]


def load_plugins(module_names: Sequence[str]) -> None:
    for module_name in module_names:
        module = import_module(module_name)
        module.load()


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

Но если изменить содержимоей файла `module_names.txt` на:

```text
congratulations_app.messengers.whatsapp
congratulations_app.congratulations_services.english
```

Получим вывод:

```text
Message 'Happy birthday, Maria!' sent to 'Maria' via WhatsApp.
```

### Сторонние плагины

Теперь рассмотрим интеграцию в приложение сторонних плагинов. Например, новый заказчик хочет использовать приложение для поздравлений сотрудников с днем рождения, но он не хочет использовать ни один из уже реализованных мессенджеров, а вместо них хочет использовать свой внутренний корпоративный мессенджер. В месте с тем этот заказчик против включения реализации своего корпоративного мессенджера в кодовую базу приложения. Даже такой случай не является проблемой для библиотеки 
__ioc__ в связке с системой плагинов. Для решения данной задачи необходимо создать отдельный проект. Его структура будет выглядеть следующим образом:

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

Рассмотрим реализацию модуля `src/secret_corporation_plugin/messengers/secret_corporation.py`. Как можно видеть, она ничем принципиально не отличается от реализации двух других мессенджеров: `Telegram` и `WhatsApp`, включенных в кодовую базу приложения.

```python
# src/secret_corporation_plugin/messengers/secret_corporation.py

from ioc.context import add_factory
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

Затем, для того чтобы использовать эту реализацию мессенджера в приложении, необходимо установить пакет `secret_corporation_plugin` с помощью команды `python setup.py install .` в корневой директории проекта с этим мессенджером. Далее в конфигурационном файле `module_names.txt` в качестве модуля с мессенджером указать `secret_corporation_plugin.messengers.secret_corporation`. В результате содержимое файла `module_names.txt` может выглядеть следующим образом:

```text
secret_corporation_plugin.messengers.secret_corporation
congratulations_app.congratulations_services.russian
```

И при запуске приложения с таким содержимым файла `module_names.txt` получим следующий вывод:

```text
Message 'С днем рождения, Maria!' sent to 'Maria' via Secret Corporation Messenger.
```

Как можно видеть в качестве мессенджера используется `SecretCorporationMessenger`. Чтобы этого добиться не потребовалось изменять код приложения, а вместо этого оказалось достаточно лишь добавить другую реализацию мессенджера в другом проекте и изменить конфигурационный файл.


## Основные возможности

* Полный контроль над созданием зависимостей.
* Поддержка статического анализа кода.
* Передача параметров в фабрики
* По одному и тому же интерфейсу фабрики можно зарегать две

* Гибкое добавление дополнительного функционала.

* Поддержка вложенных IOC контейнеров.

TODO:
* Добавить кучу примерчиков (декораторы, параметры и интеграция с FastAPI)
