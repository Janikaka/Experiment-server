import configparser
import os

from paste.deploy import loadapp
from waitress import serve

# TODO: Automate initializedb.py to run after deployment
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    # This part is Heroku specific!
    db_url = os.environ['DATABASE_URL']
    # If enviroment contains DATABASE_URL, add it to the production configuration
    # file.
    if db_url != None:
        parser = configparser.SafeConfigParser()
        parser.read('production.ini')
        parser.set('app:main', 'sqlalchemy.url', db_url)
        with open('production.ini', 'w') as configfile:
            parser.write(configfile)
    # Heroku specific part ends

    app = loadapp('config:production.ini', relative_to='.')

    serve(app, host='0.0.0.0', port=port)
