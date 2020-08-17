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
    "pytest==5.4.1",
    "pytest-asyncio==0.10.0",
    "coverage==5.0.4",
]


setup(
    name="ioc",
    version=__version__,
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
