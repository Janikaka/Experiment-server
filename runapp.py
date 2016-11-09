import os

from paste.deploy import loadapp
from waitress import serve

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app = loadapp('config:production.ini', relative_to='.')

    settings = {}
    settings['sqlalchemy.url'] = os.environ['DATABASE_URL']
    settings['pyramid.includes'] = ['pyramid_tm']
    settings['pyramid.reload_templates'] = false
    settings['pyramid.debug_authorization'] = false
    settings['pyramid.debug_notfound'] = false
    settings['pyramid.debug_routematch'] = false
    settings['pyramid.default_locale_name'] = en
    settings['pyramid.includes'] = pyramid_swagger

    pyramid_swagger.use_models = True

    serve(experiment_server.main({}, **settings), host='0.0.0.0', port=port)    
