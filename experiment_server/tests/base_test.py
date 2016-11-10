import unittest
import transaction

from pyramid import testing
from .db import DatabaseInterface
from ..models import (Experiment, Client, DataItem, ExperimentGroup, Configuration,

                      Application, ConfigurationKey, Operator, RangeConstraint, ExclusionConstraint)


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={
            'sqlalchemy.url': 'sqlite:///:memory:'
        })
        self.config.include('..models')
        self.config.include('..routes')
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
        self.DB = DatabaseInterface(self.dbsession)

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

        op3 = Operator(math_value='def', human_value='must define')
        Operator.save(op3)

        rc1 = RangeConstraint(configurationkey=confk2, operator=op2, value=1)
        RangeConstraint.save(rc1)

        rc2 = RangeConstraint(configurationkey=confk2, operator=op1, value=5)
        RangeConstraint.save(rc2)

        exc1 = ExclusionConstraint(first_configurationkey=confk1, first_operator=op3,
                                   first_value_a=None, first_value_b=None,
                                   second_configurationkey=confk2, second_operator=None,
                                   second_value_a=None, second_value_b=None)
        ExclusionConstraint.save(exc1)

        exc2 = ExclusionConstraint(first_configurationkey=confk1, first_operator=op3,
                                   first_value_a=None, first_value_b=None,
                                   second_configurationkey=confk2, second_operator=op2,
                                   second_value_a='2', second_value_b=None)
        ExclusionConstraint.save(exc2)

        expgroup1 = self.DB.create_experimentgroup(
            {'name': 'Group A'
             })
        expgroup2 = self.DB.create_experimentgroup(
            {'name': 'Group B'
             })

        conf1 = self.DB.create_configuration(
            {'key': 'v1',
             'value': 0.5,
             'experimentgroup': expgroup1
             })
        conf2 = self.DB.create_configuration(
            {'key': 'v2',
             'value': True,
             'experimentgroup': expgroup1
             })
        conf3 = self.DB.create_configuration(
            {'key': 'v1',
             'value': 1.0,
             'experimentgroup': expgroup2
             })
        conf4 = self.DB.create_configuration(
            {'key': 'v2',
             'value': False,
             'experimentgroup': expgroup2
             })

        experiment = self.DB.create_experiment(
            {'name': 'Test experiment',
             'application': app1,
             'startDatetime': '2016-01-01 00:00:00',
             'endDatetime': '2017-01-01 00:00:00',
             'experimentgroups': [expgroup1, expgroup2]
             })

        client1 = self.DB.create_client(
            {'clientname': 'First client',
             'experimentgroups': [expgroup1]
             })
        client2 = self.DB.create_client(
            {'clientname': 'Second client',
             'experimentgroups': [expgroup2]
             })

        dt1 = self.DB.create_dataitem(
            {'key': 'key1',
             'value': 10,
             'startDatetime': '2016-01-01 00:00:00',
             'endDatetime': '2016-01-01 01:01:01',
             'client': client1
             })
        dt2 = self.DB.create_dataitem(
            {'key': 'key2',
             'value': 0.5,
             'startDatetime': '2016-02-02 01:01:02',
             'endDatetime': '2016-02-02 02:02:02',
             'client': client1
             })
        dt3 = self.DB.create_dataitem(
            {'key': 'key3',
             'value': 'liked',
             'startDatetime': '2016-03-03 00:00:00',
             'endDatetime': '2016-03-03 03:03:03',
             'client': client2
             })
        dt4 = self.DB.create_dataitem(
            {'key': 'key4',
             'value': False,
             'startDatetime': '2016-04-04 03:03:04',
             'endDatetime': '2016-04-04 04:04:04',
             'client': client2
             })

    def tearDown(self):
        from experiment_server.models.meta import Base

        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(self.engine)

    def dummy_request(dbsession):
        return testing.DummyRequest(dbsession=dbsession)
