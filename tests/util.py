class FactoryForTest:
    def __call__(self) -> int:
        raise NotImplementedError()
