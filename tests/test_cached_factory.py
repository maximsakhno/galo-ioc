import pytest
from typing import (
    NoReturn,
)
from ioc import (
    CachedFactory,
)


def test_getting_instance() -> None:
    def f() -> object:
        return object()

    factory = CachedFactory(f)
    instance1 = factory()
    instance2 = factory()
    assert instance1 is instance2


def test_raising_exception() -> None:
    def f() -> NoReturn:
        raise Exception()

    factory = CachedFactory(f)

    with pytest.raises(Exception):
        factory()
