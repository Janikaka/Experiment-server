#!/bin/bash

export VENV=~/env
python3 -m venv $VENV
# TODO: change to 'pip install -r requirements.txt'
$VENV/bin/pip install -e .
# Dev-dependencies
$VENV/bin/pip install pytest
$VENV/bin/pip install coverage
$VENV/bin/pip install pylint
$VENV/bin/pip install --upgrade autopep8
