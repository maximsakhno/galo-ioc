import os
from asyncio import get_event_loop

from congratulations_app.startup_utils import (
    get_module_names_path,
    load_plugins,
    read_module_names,
)
from fastapi_integration.app import AppFactory
from galo_ioc import FactoryContainerImpl, get_factory
from uvicorn import Config, Server


def main() -> None:
    module_names_path = get_module_names_path()
    module_names = read_module_names(module_names_path)
    with FactoryContainerImpl():
        loop = get_event_loop()
        load_plugins(module_names)
        app_factory = get_factory(AppFactory)
        app = app_factory()
        port = int(os.getenv("SERVER_PORT", "8080"))

        config = Config(app=app, port=port, loop=loop)
        server = Server(config)
        loop.run_until_complete(server.serve())


if __name__ == "__main__":
    main()
