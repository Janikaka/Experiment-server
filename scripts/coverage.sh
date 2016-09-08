$VENV/bin/coverage run --source=experiment_server/models/,experiment_server/views/,experiment_server/scripts/ $VENV/bin/py.test
$VENV/bin/coverage report -m
