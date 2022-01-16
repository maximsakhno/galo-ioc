#!/bin/bash

set -x
set -e

black galo_ioc examples tests
isort galo_ioc examples tests
