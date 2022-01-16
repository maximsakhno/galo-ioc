from congratulations_app.congratulations_services import CongratulationsServiceFactory
from congratulations_app.startup_utils import (
    get_module_names_path,
    load_plugins,
    read_module_names,
)
from galo_ioc import FactoryContainerImpl, get_factory


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
