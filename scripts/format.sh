#!/bin/bash

set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place galo_ioc examples tests
black galo_ioc examples tests
isort galo_ioc examples tests
