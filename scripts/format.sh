#!/bin/bash

set -x
set -e

black --line-length 100 src/ tests/ examples/
