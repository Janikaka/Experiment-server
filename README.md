[![Build Status](https://travis-ci.org/TheSoftwareFactory/experiment-server.svg?branch=master)](https://travis-ci.org/TheSoftwareFactory/experiment-server)
[![Code Climate](https://codeclimate.com/github/TheSoftwareFactory/experiment-server/badges/gpa.svg)](https://codeclimate.com/github/TheSoftwareFactory/experiment-server)
[![Test Coverage](https://codeclimate.com/github/TheSoftwareFactory/experiment-server/badges/coverage.svg)](https://codeclimate.com/github/TheSoftwareFactory/experiment-server/coverage)
[![Issue Count](https://codeclimate.com/github/TheSoftwareFactory/experiment-server/badges/issue_count.svg)](https://codeclimate.com/github/TheSoftwareFactory/experiment-server)
# Experiment-server

A simple REST API server for providing runtime configurations for applications and receiving usage-related event data.

See the current API documentation from [here](https://app.swaggerhub.com/api/SoftwareFactory/experiment-server/). Remember to check the newest (highest) version.

The live API will live at heroku: [https://experiment-server2016.herokuapp.com/experiments](https://experiment-server2016.herokuapp.com/experiments). It will be autoupdated everytime master branch is updated at GitHub.

Backlog [here](https://trello.com/b/aRdMndWJ/backlog)

###Environment setup

We use virtualenv to virtualize the python installation. This will create need for a venv-directory which should be located at project root.

Deactivating virtualenv

`deactivate`

### Dependencies

- PostgresSQL for production `brew install postgresql`

- sqlite for development

###Getting Started
---------------

Clone this repository

- Install projects only external dependency
`pip install virtualenv`

- Setup the environment (from the project root folder):
`./scripts/setup-environment.sh`

- Start virtualenv
`source venv/bin/activate`

- Install dependencies to virtual env (venv-fold)
`pip install -r requirements.txt`

- Running the next command might be required in some cases
`python setup.py develop`

- Initialize database:
`initialize_Experiment-server_db development.ini`

- Start the local server:
`pserve development.ini`

- Install hooks (from the project root folder):
`./scripts/install-precommit-hooks.sh`


Run tests:

`pytest experiment_server/tests`

###Publishing to production

In case there are no shcema changes:
- Push to GitHub and to this projects master branch. The rest will be automatic

In case the database schema has changed
- `initialize_Experiment-server_db production.ini sqlalchemy.url=DATABASE_URL`. This will establish new via `/experiment_server/scripts/initializedb.py`. Remember to first clean the production database or it will not make modifications to it.


###Work flow

- Take a task from Trello (card)
- Create a new branch for it `git branch <task_name>`
- Start working only that branch
- Rebase often with the master `git checkout master` `git pull` `git checkout <task_name>` `git rebase master`
- Fix all the conflicts
- TEST!
- When rebasing is done. Save your work globally `git push origin <task_name>`
- When you feel that you would like the whole team get your code: Make a pull-request
- Assign somebody to code review your work
- When the code review is done merge the branch to master via GitHub.com

####Tips on adding or editing API

Since swagger_pyramid is included in this project, additionally to Python Pyramid's
documentation on adding new API paths, keeping up to date api_docs/swagger.json is 
essential. Adding a new path to routes.py is not enough to make application work!
Added path must be added to swagger.json and specify values it returns. Please keep
[Swagger API]((https://app.swaggerhub.com/api/SoftwareFactory/experiment-server/))
updated.
