from argparse import ArgumentParser
from importlib import import_module
from typing import Sequence

__all__ = [
    "get_module_names_path",
    "read_module_names",
    "load_plugins",
]


def get_module_names_path() -> str:
    parser = ArgumentParser()
    parser.add_argument("--module-names-path", required=False, default="module_names.txt")
    namespace = parser.parse_args()
    return namespace.module_names_path


def read_module_names(module_names_path: str) -> Sequence[str]:
    with open(module_names_path, mode="r") as file:
        return [
            stripped_name
            for stripped_name in (name.strip() for name in file.readlines())
            if stripped_name and not stripped_name.startswith("#")
        ]


def load_plugins(module_names: Sequence[str]) -> None:
    for module_name in module_names:
        module = import_module(module_name)
        module.load()
