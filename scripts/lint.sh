#!/bin/bash

flake8 src/ tests/
black --check --line-length 100 src/ tests/ examples/
