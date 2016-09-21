from pyramid.config import Configurator
from sqlalchemy import orm
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy import engine_from_config

import experiment_server.database.orm as A

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    settings = config.get_settings()
    engine = engine_from_config(settings, 'sqlalchemy.')
    A.DBSession = orm.scoped_session(
        orm.sessionmaker(extension=ZopeTransactionExtension()))
    A.DBSession.configure(bind=engine)


    config.include('pyramid_jinja2')
    config.include('.models')
    config.include('.routes')
    config.scan()
    return config.make_wsgi_app()
