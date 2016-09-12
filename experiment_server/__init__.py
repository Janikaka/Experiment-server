from pyramid.config import Configurator
from experiment_server.models import initialize_sql
from sqlalchemy import engine_from_config
import datetime

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.include('.models')
    config.include('.routes')
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    config.scan()
    return config.make_wsgi_app()
