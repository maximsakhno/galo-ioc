from setuptools import setup, find_packages


test_requires = [
    "pytest==6.2.5",
    "pytest-asyncio==0.16.0",
    "coverage==6.0.2",
]


setup(
    name="ioc",
    version="0.15.0",
    author="Maxim Sakhno",
    author_email="maxim.sakhno@iqtek.ru",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    tests_require=test_requires,
    extras_require={
        "test": test_requires,
    },
)
