from setuptools import setup, find_packages


dev_requires = [
    "flake8==4.0.1",
    "flake8-quotes==3.3.1",
    "flake8-import-order==0.18.1",
    "black==21.12b0",
]


test_requires = [
    "pytest==6.2.5",
    "pytest-cov==3.0.0",
    "pytest-asyncio==0.17.0",
]


setup(
    name="galo-ioc",
    version="0.15.0",
    author="Maxim Sakhno",
    author_email="maxim.sakhno@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    tests_require=test_requires,
    extras_require={
        "dev": dev_requires,
        "test": test_requires,
    },
)
