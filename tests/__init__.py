from ioc import register
from ioc import resolve


register("hello")
assert resolve(str) == "hello"
assert resolve(object) == "hello"


register(int)
assert resolve(int) == 0
assert resolve(object) == 0


def resolve_str() -> str:
    return "world"


register(resolve_str)
assert resolve(str) == "world"
assert resolve(object) == "world"


class StrResolver:
    __slots__ = ()

    def __call__(self) -> str:
        return "WORLD"


register(StrResolver())
assert resolve(str) == "WORLD"
assert resolve(object) == "WORLD"

