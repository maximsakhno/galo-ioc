# Galo-IOC

![test workflow](https://github.com/maximsakhno/galo-ioc/actions/workflows/test.yml/badge.svg)
[![codecov](https://codecov.io/gh/maximsakhno/galo-ioc/branch/master/graph/badge.svg?token=4S2MSEZ06Z)](https://codecov.io/gh/maximsakhno/galo-ioc)
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

🇷🇺[Russian version](README_ru.md)

## Description

A plugin system is well suited for creating flexible and extensible applications. In such a system, plugins are responsible for creating and binding application objects to each other (for example, various implementations of services or repositories). To do this, you need to have a storage of all objects. The [Service Locator](https://martinfowler.com/articles/injection.html#UsingAServiceLocator) pattern copes with this role perfectly, and the Galo-IOC project is an easy-to-use and lightweight implementation of it.

The plugin system together with Galo-IOC will help if necessary:
* conveniently enable/disable parts of the application functionality;
* install the application to several clients, some of whom must have some functionality individually;
* extend the application by installing third-party packages.

## Main features

* In [standard implementation](https://martinfowler.com/articles/injection.html#ADynamicServiceLocator) of the Service Locator pattern, a single instance of each class is stored. In this library, instead of an instance, a factory is stored, which allows you to flexibly manage the creation of objects. 
* To get objects of the same type, you can register several factory implementations and choose between them. 
* Support for passing parameters when calling the factory.
* Support for static code analysis. Thanks to this, the IDE suggests the names and types of parameters, as well as the type of the returned result when calling factories, which greatly simplifies writing code and avoids stupid mistakes.
* Support for decorators for factories, with which you can influence the creation of objects. For example, add logging for all created objects or add caching for objects of some type.

It is worth noting that Service Locator [is an antipattern](https://blog.ploeh.dk/2010/02/03/ServiceLocatorisanAnti-Pattern/). Its disadvantages include hiding dependencies. The examples below show a way to use this library, reducing the disadvantages of the Service Locator pattern to a minimum: Service Locator is used only in plugins, but not in the application classes. In the application classes, dependencies are explicitly specified in the constructors.

## Usage examples

To demonstrate the capabilities of the library, consider the following example. An IT company is developing a product that allows their customers — other companies — to congratulate employees on birthday via a messenger. Among the customers there are companies from different countries, and the list of messengers used includes WhatsApp, Telegram and internal corporate messengers of companies.

### Plugin system

This library works well with any plugin system, in which plugins allow you to create and bind application objects (services, repositories) with each other. This library does not provide an implementation of the plugin system, because it is not its responsibility. To use this library, you will have to take a ready-made implementation of the plugin system or implement it yourself. For these examples, we implement the plugin system ourselves.

This implementation of the plugin system will be very simple, but at the same time functional enough to demonstrate all the features of the Galo-IOC library. In this plugin system, the configuration file will contain the names of the modules. Each such module will contain a `load` function, which will be responsible for creating and registering application objects in the Service Locator. When the application starts, these modules will be imported, and then the `load` function will be called for each of them.

### An application for congratulating employees

#### Project structure

The project will have the following structure:

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

#### Configuration file

File `module_names.txt ` is the configuration file that lists the modules. These modules will be imported and the `load` function will be called for each of them. Example of file contents `module_names.txt`:

```
congratulations_app.messengers.telegram
congratulations_app.congratulations_services.russian
```

As you can see, Telegram is used as a messenger. If there is a need to replace the Telegram messenger with WhatsApp, for example, when installing an application to another customer with such a requirement, it will be enough to replace the line `congratulations_app.messengers.telegram` with `congratulations_app.messengers.whatsapp` in the configuration file of the new customer. In this way, you can replace any application object with any other without having to modify the code.

#### Implementation of messengers

The file `src/congratulations_app/messengers/__init__.py` contains the messenger interface — `Messenger` and the messenger factory interface — `MessengerFactory`. The factory interface is needed to specify the contract that other modules will use to get this object.

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

Let's consider one of the implementations of the messenger — Telegram, which is contained in the module `src/congratulations_app/messengers/telegram.py`. This module contains the implementation of the `Messenger` interface — `TelegramMessenger` and the `load` function. This function will be called when the application is initialized if this module is specified in the configuration file `module_names.txt`. The function creates an instance of the `TelegramMessenger` class and the factory `TelegramMessengerFactory` that returns the messenger instance. This factory is then registered in the Service Locator using the `add_factory` function from the Galo-IOC library. After that, using this factory, it will be possible to get an instance of the `Messenger` class in another module. The module contained the WhatsApp messenger is implemented in a similar way — `src/congratulations_app/messengers/whatsapp.py`.

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

#### Implementation of congratulations services

Now let's move on to one of the implementations of the congratulations service, which is contained in the module `src/congratulations_app/congratulation_services/russian.py` The `load` function in this module is responsible for creating an object of the `RussianCongratulationsService` type and registering its factory in the Services Locator. To get the `messenger` dependency, the `get_factory` function is used. It allows you to access the `MessengerFactory`, which is currently registered in the Services Locator. It can be `TelegramMessengerFactory`, `WhatsAppMessengerFactory` or any other. Then an instance of the `Messenger` class is gotten by calling this factory. After that, it is passed to the constructor of the `RussianCongratulationsService` class to create it.

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

Thanks to the use of factory interfaces, static code analysis and autocompletion are supported.

![](autocomplete_example.gif)

#### Implementation of the application startup function

In the application startup function, the configuration file is read and modules are loaded. The `get_factory` function (similar to `set_factory`) accesses the container of factories in the current context. To add a container of factories to the current context, use the expression `with FactoryContainerImpl():`.

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

With the contents of the file `module_names.txt`:

```text
congratulations_app.messengers.telegram
congratulations_app.congratulations_services.russian
```

The output will be:

```text
Message 'С днем рождения, Maria!' sent to 'Maria' via Telegram.
```

But if you change the contents of the file `module_names.txt` on:

```text
congratulations_app.messengers.whatsapp
congratulations_app.congratulations_services.english
```

You get the output:

```text
Message 'Happy birthday, Maria!' sent to 'Maria' via WhatsApp.
```

### Implementation of third-party plugins

Now let's look at the integration of third-party plugins into the application. For example, a new customer wants to use an application to congratulate employees on birthday, but it does not want to use any of the already implemented messengers, but instead wants to use its internal corporate messenger. At the same time, this customer is against including the implementation of its corporate messenger in the code base of the application. Even this case is not a problem for the Galo-IOC library together with the plugin system. To solve this problem, you need to create a separate project.

#### Project structure

The project structure will look like this:

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

#### Implementation of an internal corporate messenger

Consider the implementation of the module `src/secret_corporation_plugin/messengers/secret_corporation.py`. As you can see, it does not fundamentally differ from the implementation of the other two messengers: Telegram and WhatsApp, included in the code base of the application.

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

#### Integration of a third-party plugin into the application

To use the implementation of the internal corporate messenger in the application instead of `Telegram` or `WhatsApp`, you need to install the `secret_corporation_plugin` package using the command `python setup.py install .` in the root directory of the project with this messenger. Further, in the configuration file `module_names.txt` specify `secret_corporation_plugin.messengers.secret_corporation` as a module with a messenger. As a result, the contents of the file `module_names.txt` may look like this:

```text
secret_corporation_plugin.messengers.secret_corporation
congratulations_app.congratulations_services.russian
```

And when running an application with such configuration file content we get the following output:

```text
Message 'С днем рождения, Maria!' sent to 'Maria' via Secret Corporation Messenger.
```

As you can see, `SecretCorporationMessenger` is used as a messenger. To achieve this, it was not necessary to change the application code, but it was enough just to add another implementation of the messenger in another project and change the configuration file.

The full version of the example can be found at [link](https://github.com/maximsakhno/galo-ioc/tree/develop/examples/congratulations_app).

## More examples

More examples can be found at [link](https://github.com/maximsakhno/galo-ioc/tree/develop/examples).

* [loggers](https://github.com/maximsakhno/galo-ioc/tree/develop/examples/loggers) contains an example of a factory with input arguments.
* [congratulations_service_audit](https://github.com/maximsakhno/galo-ioc/tree/develop/examples/congratulations_service_audit) contains an example of using a decorator. The decorator is used for logging of input arguments for the `CongratulationsService`.

* [fastapi_integration](https://github.com/maximsakhno/galo-ioc/tree/develop/examples/fastapi_integration) contains an example of integration with the FastAPI web framework. This example implements:
  * two error handlers: text and json;
  * two user repositories: Memory and PostgreSQL;
  * two authentication methods: Basic authentication and OAuth 2;
  * and other functionality.

  You can select the used implementations of the error handler, the user repository, and the authentication method in the configuration file `module_names.txt `.
