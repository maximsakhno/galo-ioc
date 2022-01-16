from setuptools import find_packages, setup

setup(
    name="congratulations-app",
    version="0.1.0",
    author="Maxim Sakhno",
    author_email="maxim.sakhno@iqtek.ru",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
