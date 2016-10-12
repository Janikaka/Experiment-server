import unittest
import transaction

from pyramid import testing
from .database_data import DatabaseData
from ..models import (Experiment, User, DataItem, ExperimentGroup, Configuration,
                      Application, ConfigurationKey, Operator, RangeConstraint, ExclusionConstraint)


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={
            'sqlalchemy.url': 'sqlite:///:memory:'
        })
        self.config.include('..models')
        settings = self.config.get_settings()

        from experiment_server.models import (
            get_engine,
            get_session_factory,
            get_tm_session
            )

        self.engine = get_engine(settings)
        session_factory = get_session_factory(self.engine)
        self.dbsession = get_tm_session(session_factory, transaction.manager)
        import experiment_server.database.orm as orm_config
        orm_config.DBSession = self.dbsession

    def init_database(self):
        from experiment_server.models.meta import Base
        Base.metadata.create_all(self.engine)

    def init_databaseData(self):

        DatabaseData.create_database(self)

    def tearDown(self):
        from experiment_server.models.meta import Base

        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(self.engine)

    def dummy_request(dbsession):
        return testing.DummyRequest(dbsession=dbsession)

