# Experiment-server

A simple REST API server for providing runtime configurations for applications and receiving usage-related event data.

###Getting Started
---------------

$VENV/bin/pip install -e .

$VENV/bin/initialize_Experiment-server_db development.ini

$VENV/bin/pserve development.ini

###Trying the REST API using `curl`

Creating a new experiment:

    $ curl -H "Content-Type: application/json" -X POST -d '{"name": "First experiment", "experimentgroups": ["group A", "group B"]}' http://localhost:6543/experiments

Deleting an experiment:

    $ curl -H "Content-Type: application/json" -X DELETE -d '' http://localhost:6543/experiments/1
