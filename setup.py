from os import path
from setuptools import setup
from setuptools import find_packages
from requirements import read
from requirements import Requirements


requirements: Requirements = read(file=path.join("requirements", "prod.txt"))


setup(
    name="ioc",
    version="0.0.3",
    author="Maxim Sakhno",
    author_email="maxim.sakhno@iqtek.ru",
    packages=find_packages(),
    install_requires=requirements.install_requires,
    dependency_links=requirements.dependency_links,
)
