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
        return [stripped_name
                for stripped_name in (name.strip() for name in file.readlines())
                if not stripped_name.startswith("#")]


def load_plugins(module_names: Sequence[str]) -> None:
    for module_name in module_names:
        module = import_module(module_name)
        module.load()


if __name__ == "__main__":
    main()
