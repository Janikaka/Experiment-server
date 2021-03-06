import datetime
import unittest
import transaction
import uuid

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

        app1 = Application(name='App 1', apikey=str(uuid.uuid4()))
        Application.save(app1)

        app2 = Application(name='App 2', apikey=str(uuid.uuid4()))
        Application.save(app2)

        confk1 = ConfigurationKey(application=app1, name='highscore', type='boolean')
        ConfigurationKey.save(confk1)

        confk2 = ConfigurationKey(application=app1, name='difficulty', type='integer')
        ConfigurationKey.save(confk2)

        op1 = Operator(id=1, math_value='=', human_value='equals')
        op2 = Operator(id=2, math_value='<=', human_value='less or equal than')
        op3 = Operator(id=3, math_value='<', human_value='less than')
        op4 = Operator(id=4, math_value='>=', human_value='greater or equal than')
        op5 = Operator(id=5, math_value='>', human_value='greater than')
        op6 = Operator(id=6, math_value='!=', human_value='not equal')
        op7 = Operator(id=7, math_value='[]', human_value='inclusive')
        op8 = Operator(id=8, math_value='()', human_value='exclusive')
        op9 = Operator(id=9, math_value='def', human_value='must define')
        op10 = Operator(id=10, math_value='ndef', human_value='must not define')

        Operator.save(op1)
        Operator.save(op2)
        Operator.save(op3)
        Operator.save(op4)
        Operator.save(op5)
        Operator.save(op6)
        Operator.save(op7)
        Operator.save(op8)
        Operator.save(op9)
        Operator.save(op10)

        rc1 = RangeConstraint(configurationkey=confk1, operator=op1, value=True)
        RangeConstraint.save(rc1)

        rc2 = RangeConstraint(configurationkey=confk2, operator=op3, value=5)
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
        expgroup3 = ExperimentGroup(id=42, name='Group Ö')
        ExperimentGroup.save(expgroup3)

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
        conf5 = Configuration(key='v9', value=False, experimentgroup_id=expgroup3.id)
        Configuration.save(conf5)

        experiment = Experiment(name='Test experiment', application_id=1,
        startDatetime=datetime.datetime.strptime('2016-01-01 00:00:00', "%Y-%m-%d %H:%M:%S"),
        endDatetime=datetime.datetime.strptime('2017-01-01 00:00:00', "%Y-%m-%d %H:%M:%S"),
        experimentgroups=[expgroup1, expgroup2])

        experiment = Experiment(name='Better Test Experiment', application_id=2,
        startDatetime=datetime.datetime.strptime('2016-01-01 00:00:00', "%Y-%m-%d %H:%M:%S"),
        endDatetime=datetime.datetime.strptime('2017-01-01 00:00:00', "%Y-%m-%d %H:%M:%S"),
        experimentgroups=[expgroup3])

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
