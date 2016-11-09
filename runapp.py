import ConfigParser
import os

from paste.deploy import loadapp
from waitress import serve

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app = loadapp('config:production.ini', relative_to='.')

    parser = ConfigParser.SafeConfigParser()
    parser.read('production.ini')
    parser.set('app:main', 'sqlalchemy.url', os.environ['DATABASE_URL'])
    parser.write('production.ini')

    serve(app, host='0.0.0.0', port=port)
