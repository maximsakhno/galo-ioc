#!/bin/bash

set -x

pytest --cov galo_ioc --cov-report xml tests
