from sqlalchemy import engine_from_config
from sqlalchemy.orm import configure_mappers
from sqlalchemy.orm import sessionmaker
import zope.sqlalchemy
# import or define all models here to ensure they are attached to the
# Base.metadata prior to any initialization routines
from experiment_server.models.experiments import Experiment
from experiment_server.models.users import User
from experiment_server.models.dataitems import DataItem
from experiment_server.models.experimentgroups import ExperimentGroup
from experiment_server.models.db import DatabaseInterface
from experiment_server.models.configurations import Configuration
from experiment_server.models.applications import Application


# run configure_mappers after defining all of the models to ensure
# all relationships can be setup
configure_mappers()


def get_engine(settings, prefix='sqlalchemy.'):
    return engine_from_config(settings, prefix)

def get_session_factory(engine):
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory

def get_tm_session(session_factory, transaction_manager):
    """
    Get a ``sqlalchemy.orm.Session`` instance backed by a transaction.

    This function will hook the session to the transaction manager which
    will take care of committing any changes.

    - When using pyramid_tm it will automatically be committed or aborted
      depending on whether an exception is raised.

    - When using scripts you should wrap the session in a manager yourself.
      For example::

          import transaction

          engine = get_engine(settings)
          session_factory = get_session_factory(engine)
          with transaction.manager:
              dbsession = get_tm_session(session_factory, transaction.manager)

    """
    dbsession = session_factory()
    zope.sqlalchemy.register(
        dbsession, transaction_manager=transaction_manager)
    return dbsession

def includeme(config):
    """
    Initialize the model for a Pyramid app.

    Activate this setup using ``config.include('Experiment-server.models')``.

    """
    settings = config.get_settings()
    # use pyramid_tm to hook the transaction lifecycle to the request
    config.include('pyramid_tm')

    engine = get_engine(settings)
    session_factory = get_session_factory(engine)
    config.registry['dbsession_factory'] = session_factory

    import experiment_server.database.orm as orm_config

    # make request.dbsession available for use in Pyramid
    config.add_request_method(
        # r.tm is the transaction manager used by pyramid_tm
        lambda r: orm_config.DBSession,
        'dbsession',
        reify=True
    )
