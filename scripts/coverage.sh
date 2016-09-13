pytest --cov-report term-missing --cov=experiment_server experiment_server/tests.py
CODECLIMATE_REPO_TOKEN=81f7d3802f847de8d5d471351443281ce0dd7a6fd35e0a5141869b33417f9c8e codeclimate-test-reporter --file .coverage
