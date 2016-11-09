import os
from pyramid.config import Configurator
from sqlalchemy import orm
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy import engine_from_config

import experiment_server.database.orm as orm_config

"""
Startpoint for the app. CORS-headers are first added here.
"""


def add_cors_headers_response_callback(event):
    def cors_headers(request, response):
        response.headers.update({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST,GET,DELETE,PUT,OPTIONS',
        'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept, Authorization',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Max-Age': '1728000',
        'Content-Type': 'application/json',
        })
    event.request.add_response_callback(cors_headers)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    env_db_address = os.environ["DATABASE_URL"]
    if env_db_address != None:
        settings["sqlalchemy.url"] = env_db_adress

    config = Configurator(settings=settings)

    settings = config.get_settings()

    engine = engine_from_config(settings, 'sqlalchemy.')

    orm_config.DBSession = orm.scoped_session(
        orm.sessionmaker(extension=ZopeTransactionExtension(), autoflush=True))
    orm_config.DBSession.configure(bind=engine)

    from pyramid.events import NewRequest
    config.add_subscriber(add_cors_headers_response_callback, NewRequest)

    config.include('pyramid_jinja2')
    config.include('.models')
    config.include('.routes')
    config.scan()

    settings['pyramid_swagger.enable_path_validation'] = False

    return config.make_wsgi_app()
