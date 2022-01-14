#!/bin/bash

set -x
set -e

flake8 src/ tests/
black --check --line-length 100 src/ tests/ examples/
bandit -r src/
