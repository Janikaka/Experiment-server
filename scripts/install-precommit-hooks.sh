#!/bin/bash

cd scripts
cp ./hooks/pre-commit ../.git/hooks
cd ..
chmod u+x .git/hooks/pre-commit
