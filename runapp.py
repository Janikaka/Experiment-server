import os

from configparser import SafeConfigParser
from paste.deploy import loadapp
from waitress import serve

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app = loadapp('config:production.ini', relative_to='.')

    db_address = os.environ['DATABASE_URL']

    if db_address != None:
        print("***\n" + db_address + "\***")
        parser = SafeConfigParser()
        parser.read('production.ini')
        parser.set('app:main', 'sqlalchemy.url', db_address)

    serve(app, host='0.0.0.0', port=port)
