import datetime
import unittest
import transaction

from pyramid import testing
from ..models import (Experiment, User, DataItem, ExperimentGroup, Configuration,
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

        expgroup1 = ExperimentGroup(name='Group A')
        ExperimentGroup.save(expgroup1)

        expgroup2 = ExperimentGroup(name='Group B')
        ExperimentGroup.save(expgroup2)

        conf1 = Configuration(key='v1', value=0.5, experimentgroup=expgroup1)
        Configuration.save(conf1)

        conf2 = Configuration(key='v2', value=True, experimentgroup=expgroup1)
        Configuration.save(conf2)

        conf3 = Configuration(key='v1', value=1.0, experimentgroup=expgroup2)
        Configuration.save(conf3)

        conf4 = Configuration(key='v2', value=False, experimentgroup=expgroup2)
        Configuration.save(conf4)

        year1 = datetime.datetime(2016, 1, 1, 0, 0, 0)
        year2 = datetime.datetime(2017, 1, 1, 0, 0, 0)
        experiment = Experiment(name='Test experiment', application=app1,
                                startDatetime=year1,
                                endDatetime=year2,
                                size=100,
                                experimentgroups=[expgroup1, expgroup2])
        Experiment.save(experiment)

        user1 = User(username='First user', experimentgroups=[expgroup1])
        User.save(user1)

        user2 = User(username='Second user', experimentgroups=[expgroup2])
        User.save(user2)

        start1 = datetime.datetime(2016, 1, 1, 0, 0, 0)
        end1 = datetime.datetime(2016, 1, 1, 1, 1, 1)
        dt1 = DataItem(key='key1', value=10, startDatetime=start1,
                        endDatetime=end1, user=user1)
        DataItem.save(dt1)

        start2 = datetime.datetime(2016, 2, 2, 1, 1, 2)
        end2 = datetime.datetime(2016, 2, 2, 2, 2, 2)
        dt2 = DataItem(key='key2', value=0.5, startDatetime=start2,
                        endDatetime=end2, user=user1)
        DataItem.save(dt2)

        start3 = datetime.datetime(2016, 3, 3, 0, 0, 0)
        end3 = datetime.datetime(2016, 3, 3, 3, 3, 3)
        dt3 = DataItem(key='key3', value='liked', startDatetime=start3,
                        endDatetime=end3, user=user2)
        DataItem.save(dt3)

        start4 = datetime.datetime(2016, 4, 4, 3, 3, 4)
        end4 = datetime.datetime(2016, 4, 4, 4, 4, 4)
        dt4 = DataItem(key='key4', value=False, startDatetime=start4,
                        endDatetime=end4, user=user2)
        DataItem.save(dt4)

    def tearDown(self):
        from experiment_server.models.meta import Base

        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(self.engine)

    def dummy_request(dbsession):
        return testing.DummyRequest(dbsession=dbsession)
