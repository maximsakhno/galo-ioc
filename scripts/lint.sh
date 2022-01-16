#!/bin/bash

set -x
set -e

flake8 galo_ioc examples tests
black galo_ioc examples tests --check
isort galo_ioc examples tests --check-only
bandit galo_ioc -r
