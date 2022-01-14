#!/bin/bash

set -x
set -e

installed_dependencies=$(pip freeze | grep --invert-match '\-e')
if [[ $installed_dependencies ]]; then
    echo "$installed_dependencies" | xargs pip uninstall -y
fi

pip install -e .[dev,test]
