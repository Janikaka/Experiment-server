import unittest
import transaction

from pyramid import testing

def dummy_request(dbsession):
    return testing.DummyRequest(dbsession=dbsession)

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={
            'sqlalchemy.url': 'sqlite:///:memory:'
        })
        self.config.include('.models')
        settings = self.config.get_settings()

        from .models import (
            get_engine,
            get_session_factory,
            get_tm_session,
            )

        self.engine = get_engine(settings)
        session_factory = get_session_factory(self.engine)
        self.session = get_tm_session(session_factory, transaction.manager)

    def init_database(self):
        from .models.meta import Base

        Base.metadata.create_all(self.engine)

    def tearDown(self):
        from .models.meta import Base

        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(self.engine)

class TestExperiments(BaseTest):

    def setUp(self):
        super(TestExperiments, self).setUp()
        self.init_database()

        from .models import Experiments

        experiment1 = Experiments(name='first experiment')
        self.session.add(experiment1)
        experiment2 = Experiments(name='second experiment')
        self.session.add(experiment2)

    def test_add_experiments(self):
        from .models import Experiments

        exp1 = self.session.query(Experiments).filter_by(name='first experiment').one()
        self.assertEqual(exp1.name, 'first experiment')
        self.assertEqual(exp1.id, 1)
        exp2 = self.session.query(Experiments).filter_by(name='second experiment').one()
        self.assertEqual(exp2.name, 'second experiment')
        self.assertEqual(exp2.id, 2)
        self.assertEqual(len(self.session.query(Experiments).all()), 2)


class TestUsers(BaseTest):

    def setUp(self):
        super(TestUsers, self).setUp()
        self.init_database()

        from .models import Users

        user1 = Users(username='first user', password='first password')
        self.session.add(user1)
        user2 = Users(username='second user', password='second password')
        self.session.add(user2)

    def test_add_users(self):
        from .models import Users

        user1 = self.session.query(Users).filter_by(username='first user').one()
        self.assertEqual(user1.username, 'first user')
        self.assertEqual(user1.id, 1)
        user2 = self.session.query(Users).filter_by(username='second user').one()
        self.assertEqual(user2.username, 'second user')
        self.assertEqual(user2.id, 2)
        self.assertEqual(len(self.session.query(Users).all()), 2)

class TestDataItems(BaseTest):

    def setUp(self):
        super(TestDataItems, self).setUp()
        self.init_database()

        from .models import Users
        from .models import DataItems

        user1 = Users(username='first user', password='first password')
        self.session.add(user1)
        user2 = Users(username='second user', password='second password')
        self.session.add(user2)

        usr1 = self.session.query(Users).filter_by(username='first user').one()
        usr2 = self.session.query(Users).filter_by(username='second user').one()

        dataItem1 = DataItems(user_id=usr1.id, user=usr1, value=10)
        dataItem2 = DataItems(user_id=usr1.id, user=usr1, value=20)
        dataItem3 = DataItems(user_id=usr2.id, user=usr2, value=30)
        dataItem4 = DataItems(user_id=usr2.id, user=usr2, value=40)

        self.session.add(dataItem1)
        self.session.add(dataItem2)
        self.session.add(dataItem3)
        self.session.add(dataItem4)

    def test_addDataItems(self):
        from .models import DataItems

        self.assertEqual(len(self.session.query(DataItems).all()), 4)


    def test_added_dataItems(self):
        from .models import DataItems

        dataItem1 = self.session.query(DataItems).filter_by(id=1).one()
        dataItem2 = self.session.query(DataItems).filter_by(id=2).one()
        dataItem3 = self.session.query(DataItems).filter_by(id=3).one()
        dataItem4 = self.session.query(DataItems).filter_by(id=4).one()

        self.assertEqual(dataItem1.user_id, 1);
        self.assertEqual(dataItem2.user_id, 1);
        self.assertEqual(dataItem3.user_id, 2);
        self.assertEqual(dataItem4.user_id, 2);
        self.assertEqual(dataItem1.value, 10);
        self.assertEqual(dataItem2.value, 20);
        self.assertEqual(dataItem3.value, 30);
        self.assertEqual(dataItem4.value, 40);

class TestExperimentGroups(BaseTest):

    def setUp(self):
        super(TestExperimentGroups, self).setUp()
        self.init_database()

        from .models import Experiments
        from .models import ExperimentGroups

        experiment1 = Experiments(name='first experiment')
        experiment2 = Experiments(name='second experiment')
        self.session.add(experiment1)
        self.session.add(experiment2)

        experiment1 = self.session.query(Experiments).filter_by(name='first experiment').one()
        experiment2 = self.session.query(Experiments).filter_by(name='second experiment').one()

        experimentGroup1 = ExperimentGroups(experiment_id=experiment1.id, experiment = experiment1, name='exp1groupA')
        experimentGroup2 = ExperimentGroups(experiment_id=experiment1.id, experiment = experiment1, name='exp1groupB')
        experimentGroup3 = ExperimentGroups(experiment_id=experiment2.id, experiment = experiment2, name='exp2groupA')
        experimentGroup4 = ExperimentGroups(experiment_id=experiment2.id, experiment = experiment2, name='exp2groupB')

        self.session.add(experimentGroup1)
        self.session.add(experimentGroup2)
        self.session.add(experimentGroup3)
        self.session.add(experimentGroup4)

    def test_add_experimentGroups(self):
        from .models import ExperimentGroups

        self.assertEqual(len(self.session.query(ExperimentGroups).all()), 4)
        
    def test_added_experimentGroups(self):
        from .models import ExperimentGroups
        from .models import Experiments

        expGroup1 = self.session.query(ExperimentGroups).filter_by(id=1).one()
        expGroup2 = self.session.query(ExperimentGroups).filter_by(id=2).one()
        expGroup3 = self.session.query(ExperimentGroups).filter_by(id=3).one()
        expGroup4 = self.session.query(ExperimentGroups).filter_by(id=4).one()

        self.assertEqual(expGroup1.experiment_id, 1)
        self.assertEqual(expGroup2.experiment_id, 1)
        self.assertEqual(expGroup3.experiment_id, 2)
        self.assertEqual(expGroup4.experiment_id, 2)
        self.assertEqual(expGroup1.name, 'exp1groupA')
        self.assertEqual(expGroup2.name, 'exp1groupB')
        self.assertEqual(expGroup3.name, 'exp2groupA')
        self.assertEqual(expGroup4.name, 'exp2groupB')
"""
class TestDataItems_Experiments(BaseTest):

    def setUp(self):
        super(TestDataItems_Experiments, self).setUp()
        self.init_database()

        experiment1 = Experiments(name='first experiment')
        experiment2 = Experiments(name='second experiment')
        self.session.add(experiment1)
        self.session.add(experiment2)

        user1 = Users(username='first user', password='first password')
        self.session.add(user1)
        user2 = Users(username='second user', password='second password')
        self.session.add(user2)

        dataItem1 = DataItems(user_id=user1.id, user=user1, value=10, experiments.append(experiment1))
        dataItem2 = DataItems(user_id=user1.id, user=user1, value=20, experiments.append(experiment1))
        dataItem3 = DataItems(user_id=user2.id, user=user2, value=30, experiments.append(experiment2))
        dataItem4 = DataItems(user_id=user2.id, user=user2, value=40, experiments.append(experiment2))
        self.session.add(dataItem1)
        self.session.add(dataItem2)
        self.session.add(dataItem3)
        self.session.add(dataItem4)
        
"""





"""
class TestMyViewFailureCondition(BaseTest):

    def test_failing_view(self):
        from .views.default import my_view
        info = my_view(dummy_request(self.session))
        self.assertEqual(info.status_int, 500)

class TestMyViewSuccessCondition(BaseTest):

    def setUp(self):
        super(TestMyViewSuccessCondition, self).setUp()
        self.init_database()

        from .models import MyModel

        model = MyModel(name='one', value=55)
        self.session.add(model)

    def test_passing_view(self):
        from .views.default import my_view
        from .models import MyModel
        info = my_view(dummy_request(self.session))
        self.assertEqual(info['one'].name, 'one')
        self.assertEqual(info['project'], 'Experiment-server')
        self.assertEqual(self.session.query(MyModel).filter_by(name='one').one().value, 55)
"""
