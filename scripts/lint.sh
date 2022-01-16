#!/bin/bash

set -x
set -e

mypy galo_ioc tests
flake8 galo_ioc examples tests
black galo_ioc examples tests --check
isort galo_ioc examples tests --check-only
bandit galo_ioc -r
