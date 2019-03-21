from typing import List
from setuptools import setup
from setuptools import find_packages


install_requires: List[str] = [

]


test_requires: List[str] = [

]


setup(
    name="ioc",
    version="0.0.6",
    author="Maxim Sakhno",
    author_email="maxim.sakhno@iqtek.ru",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    install_requires=install_requires,
    tests_require=test_requires,
    extras_require={
        "test": test_requires,
    },
)
