#!/bin/bash

set -x
set -e

pytest --cov galo_ioc --cov-report xml tests/
