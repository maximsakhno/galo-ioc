import ioc
from typing import (
    Protocol,
    cast,
)


def main() -> None:

    class IntegerService:
        __slots__ = ()

        @property
        def integer(self) -> int:
            raise NotImplementedError()

        @staticmethod
        def get_static_integer() -> int:
            raise NotImplementedError()

        @classmethod
        def get_class_integer(cls) -> int:
            raise NotImplementedError()

        def get_integer(self, value: int = 1) -> int:
            raise NotImplementedError()

    class IntegerServiceImpl(IntegerService):
        __slots__ = ()

        @property
        def integer(self) -> int:
            return 0

        @staticmethod
        def get_static_integer() -> int:
            return 1

        @classmethod
        def get_class_integer(cls) -> int:
            return 2

        def get_integer(self, value: int = 1) -> int:
            return value

    class IntegerServiceFactory(Protocol):
        __slots__ = ()

        def __call__(self) -> IntegerService:
            raise NotImplementedError()

    integer_service_factory, integer_service_factory_setter = ioc.use_factory(IntegerServiceFactory)
    integer_service = ioc.get_instance(IntegerService, integer_service_factory)

    with ioc.using_factory_container(ioc.DictFactoryContainer()):
        integer_service_factory_setter(cast(IntegerServiceFactory, lambda: IntegerServiceImpl()))
        print(integer_service.integer)
        print(integer_service.get_static_integer())
        print(integer_service.get_class_integer())
        print(integer_service.get_integer(3))


if __name__ == "__main__":
    main()
