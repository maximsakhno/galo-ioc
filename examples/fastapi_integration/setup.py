from setuptools import find_packages, setup

setup(
    name="fastapi-integration",
    version="0.1.0",
    author="Maxim Sakhno",
    author_email="maxim.sakhno@iqtek.ru",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi==0.70.0",
        "uvicorn[standard]==0.15.0",
        "python-multipart==0.0.5",
        "PyJWT==2.3.0",
        "asyncpg==0.25.0",
    ],
)
