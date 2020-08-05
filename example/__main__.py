import ioc
from typing import (
    Protocol,
    cast,
)


def main() -> None:

    class IntegerFactory(Protocol):
        __slots__ = ()

        def __call__(self, value: int) -> int:
            raise NotImplementedError()

    # integer_factory, set_integer_factory = ioc.use_factory(IntegerFactory)
    integer_factory = ioc.get_factory(IntegerFactory, "hello world")
    set_integer_factory = ioc.get_factory_setter(IntegerFactory, "hello world")

    with ioc.using_factory_container(ioc.DictFactoryContainer()):
        set_integer_factory(cast(IntegerFactory, lambda value: value))
        value = integer_factory(4)
        print(value)


if __name__ == "__main__":
    main()
