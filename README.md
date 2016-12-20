[![Build Status](https://travis-ci.org/TheSoftwareFactory/experiment-server.svg?branch=master)](https://travis-ci.org/TheSoftwareFactory/experiment-server)
[![Code Climate](https://codeclimate.com/github/TheSoftwareFactory/experiment-server/badges/gpa.svg)](https://codeclimate.com/github/TheSoftwareFactory/experiment-server)
[![Test Coverage](https://codeclimate.com/github/TheSoftwareFactory/experiment-server/badges/coverage.svg)](https://codeclimate.com/github/TheSoftwareFactory/experiment-server/coverage)
[![Issue Count](https://codeclimate.com/github/TheSoftwareFactory/experiment-server/badges/issue_count.svg)](https://codeclimate.com/github/TheSoftwareFactory/experiment-server)
# Experiment-server

A simple REST API server for providing runtime configurations for applications and receiving usage-related event data.

See the current API documentation from [here](https://app.swaggerhub.com/api/SoftwareFactory/experiment-server/). 
Remember to check the newest (highest) version.

The live API will live at heroku: 
[https://experiment-server2016.herokuapp.com](https://experiment-server2016.herokuapp.com). It will be autoupdated everytime master branch is updated at GitHub.

**Please view TODO-section at the bottom before developing anything else**

##Environment setup

We use virtualenv to virtualize the python installation. This will create need for a venv-directory which should be 
located at project root.

Deactivating virtualenv

`deactivate`

###Dependencies

- PostgresSQL for production `brew install postgresql`
- sqlite for development
- pip

###Getting Started

1. Clone this repository

2. Install projects only external dependency
`pip install virtualenv`

3. Setup the environment (from the project root folder):
`./scripts/setup-environment.sh`

4. Start virtualenv
`source venv/bin/activate`

5. Install dependencies to virtual env (venv-fold)
`pip install -r requirements.txt`

6. Running the next command might be required in some cases
`python setup.py develop`

7. Initialize database:
`initialize_Experiment-server_db development.ini`

8. Start the local server:
`pserve development.ini`

9. (Optional but still recommended) Install hooks (from the project root folder):
`./scripts/install-precommit-hooks.sh`
    - this scripts causes tests to be ran after committing: `git commit -m 'message'`


###Run tests:

- `pytest experiment_server/tests`
    - This can only be done when virtual-environment is activated

##Publishing to production

In case there are no database-schema changes:

1. Push to GitHub and to this projects master branch. The rest will be automatic
    - Notice that in case some tests fail, master branch will not be pushed to Heroku

In case the database schema has changed

1. Reset production/staging database in Heroku
2. `initialize_Experiment-server_db production.ini sqlalchemy.url=DATABASE_URL`
    - This will establish new via `/experiment_server/scripts/initializedb.py`
    - Remember to first clean the production database or it will not make modifications to it.

##Tips on editing API

Since swagger_pyramid is included in this project, additionally to Python Pyramid's
documentation on adding new API paths, keeping api_docs/swagger.json up to date is
essential. Adding a new path to routes.py is not enough to make application work!
Added path must be added to swagger.json and specify values it returns. Please keep
[Swagger API]((https://app.swaggerhub.com/api/SoftwareFactory/experiment-server/))
updated.

##TODO

- December 20th 2016:
    - POST experimentgroup: create new experimentgroup
        - now there is no way creating an ExperimentGroup. Perform this before doing anything else!
        - also consider creating a ExperimentGroup by default when creating an Experiment. This property was 
        accidentally deleted during refactoring
    - Consider hard-coding operators instead of saving them database-table
        - operators in a database brings no benefits
    - Configuration:
        - DELETE: delete configuration
        - PUT: edit configuration
    - Consider removing Swagger-dependency from the project
        - While Swagger is involved, developing this project has proved to be overly complicated
        - If decision is made to move away from Swagger, don't forget to make API-tests to cover API-addresses which Swagger 
        used to do
