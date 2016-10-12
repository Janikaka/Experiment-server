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

        app1 = Application(name='App 1')
        Application.save(app1)

        app2 = Application(name='App 2')
        Application.save(app2)

        confk1 = ConfigurationKey(application=app1, name='highscore', type='boolean')
        ConfigurationKey.save(confk1)

        confk2 = ConfigurationKey(application=app1, name='difficulty', type='integer')
        ConfigurationKey.save(confk2)

        op1 = Operator(math_value='<=', human_value='less or equal than')
        Operator.save(op1)

        op2 = Operator(math_value='>=', human_value='greater or equal than')
        Operator.save(op2)

        rc1 = RangeConstraint(configurationkey=confk2, operator=op2, value=1)
        RangeConstraint.save(rc1)

        rc2 = RangeConstraint(configurationkey=confk2, operator=op1, value=5)
        RangeConstraint.save(rc2)

        DatabaseData.create_database(self)

    def tearDown(self):
        from experiment_server.models.meta import Base

        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(self.engine)

    def dummy_request(dbsession):
        return testing.DummyRequest(dbsession=dbsession)

