#!/bin/bash

set -x
set -e

flake8 galo_ioc tests
black galo_ioc tests --check --line-length 100
bandit galo_ioc -r
