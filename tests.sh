#!/bin/bash

if [[ ! -d coverage ]]; then
    mkdir coverage
fi

pushd ..
python -m coverage run -m pythoughts.tests
python -m coverage html -d ./pythoughts/coverage
python -m coverage report
popd
