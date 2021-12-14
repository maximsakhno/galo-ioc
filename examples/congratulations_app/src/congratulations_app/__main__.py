from ioc.context import get_factory
from ioc.factory_containers.impl import FactoryContainerImpl
from congratulations_app.setup_utils import get_module_names_path, read_module_names, load_plugins
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
