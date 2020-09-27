from setuptools import (
    setup,
    find_packages,
)
from ioc import (
    __version__,
)


install_requires = [

]


prod_requires = [
    *install_requires,
]


test_requires = [
    *prod_requires,
    "mypy==0.782",
    "pytest==6.0.1",
    "pytest-asyncio==0.14.0",
    "coverage==5.2.1",
]


setup(
    name="ioc",
    version="0.8.0",
    author="Maxim Sakhno",
    author_email="maxim.sakhno@iqtek.ru",
    packages=find_packages(include=["ioc", "ioc.*"]),
    install_requires=install_requires,
    tests_require=test_requires,
    extras_require={
        "prod": prod_requires,
        "test": test_requires,
    },
)
