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

        dataItem1 = DataItems(user=user1, value=10)
        dataItem2 = DataItems(user=user1, value=20)
        dataItem3 = DataItems(user=user2, value=30)
        dataItem4 = DataItems(user=user2, value=40)

        self.session.add(dataItem1)
        self.session.add(dataItem2)
        self.session.add(dataItem3)
        self.session.add(dataItem4)

    def test_addDataItems(self):
        from .models import DataItems

        self.assertEqual(len(self.session.query(DataItems).all()), 4)


    def test_added_dataItems(self):
        from .models import DataItems
        from .models import Users

        dataItem1 = self.session.query(DataItems).filter_by(id=1).one()
        dataItem2 = self.session.query(DataItems).filter_by(id=2).one()
        dataItem3 = self.session.query(DataItems).filter_by(id=3).one()
        dataItem4 = self.session.query(DataItems).filter_by(id=4).one()

        user1 = self.session.query(Users).filter_by(id=1).one()
        user2 = self.session.query(Users).filter_by(id=2).one()

        self.assertEqual(dataItem1.user.id, 1);
        self.assertEqual(dataItem2.user.id, 1);
        self.assertEqual(dataItem3.user.id, 2);
        self.assertEqual(dataItem4.user.id, 2);
        self.assertEqual(dataItem1.value, 10);
        self.assertEqual(dataItem2.value, 20);
        self.assertEqual(dataItem3.value, 30);
        self.assertEqual(dataItem4.value, 40);
        self.assertEqual(len(user1.dataitems), 2)
        self.assertTrue(dataItem1 in user1.dataitems)
        self.assertTrue(dataItem2 in user1.dataitems)
        self.assertEqual(len(user2.dataitems), 2)
        self.assertTrue(dataItem3 in user2.dataitems)
        self.assertTrue(dataItem4 in user2.dataitems)

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

        experimentGroup1 = ExperimentGroups(experiment = experiment1, name='exp1groupA')
        experimentGroup2 = ExperimentGroups(experiment = experiment1, name='exp1groupB')
        experimentGroup3 = ExperimentGroups(experiment = experiment2, name='exp2groupA')
        experimentGroup4 = ExperimentGroups(experiment = experiment2, name='exp2groupB')

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

        self.assertEqual(expGroup1.experiment.name, 'first experiment')
        self.assertEqual(expGroup2.experiment.name, 'first experiment')
        self.assertEqual(expGroup3.experiment.name, 'second experiment')
        self.assertEqual(expGroup4.experiment.name, 'second experiment')

        self.assertEqual(expGroup1.name, 'exp1groupA')
        self.assertEqual(expGroup2.name, 'exp1groupB')
        self.assertEqual(expGroup3.name, 'exp2groupA')
        self.assertEqual(expGroup4.name, 'exp2groupB')

class TestUsers_ExperimentGroups(BaseTest):

    def setUp(self):
        super(TestUsers_ExperimentGroups, self).setUp()
        self.init_database()

        from .models import ExperimentGroups
        from .models import Users
        from .models import Experiments

        user1 = Users(username='first user', password='first password')
        self.session.add(user1)
        user2 = Users(username='second user', password='second password')
        self.session.add(user2)
        user3 = Users(username='third user', password='third password')
        self.session.add(user3)
        user4 = Users(username='fourth user', password='fourth password')
        self.session.add(user4)

        experiment1 = Experiments(name='first experiment')
        self.session.add(experiment1)

        experimentGroup1 = ExperimentGroups(experiment = experiment1, name='exp1groupA')
        experimentGroup2 = ExperimentGroups(experiment = experiment1, name='exp1groupB')
        experimentGroup1.users.append(user1)
        experimentGroup1.users.append(user2)
        experimentGroup2.users.append(user3)
        experimentGroup2.users.append(user4)

        self.session.add(experimentGroup1)
        self.session.add(experimentGroup2)

    def test_add_Users_Experimentgroups(self):
        from .models import ExperimentGroups
        from .models import Users

        user1 = self.session.query(Users).filter_by(id=1).one()
        user2 = self.session.query(Users).filter_by(id=2).one()
        user3 = self.session.query(Users).filter_by(id=3).one()
        user4 = self.session.query(Users).filter_by(id=4).one()

        expgroup1 = self.session.query(ExperimentGroups).filter_by(id=1).one()
        expgroup2 = self.session.query(ExperimentGroups).filter_by(id=2).one()

        self.assertEqual(len(user1.experimentgroups), 1)
        self.assertEqual(len(user2.experimentgroups), 1)
        self.assertEqual(len(user3.experimentgroups), 1)
        self.assertEqual(len(user4.experimentgroups), 1)

        self.assertEqual(len(expgroup1.users), 2)
        self.assertEqual(len(expgroup2.users), 2)

        self.assertTrue(expgroup1 in user1.experimentgroups)
        self.assertTrue(expgroup1 in user2.experimentgroups)
        self.assertTrue(expgroup2 in user3.experimentgroups)
        self.assertTrue(expgroup2 in user4.experimentgroups)

        self.assertTrue(user1 in expgroup1.users)
        self.assertTrue(user2 in expgroup1.users)
        self.assertTrue(user3 in expgroup2.users)
        self.assertTrue(user4 in expgroup2.users)

        self.assertEqual(user1.experimentgroups[0].experiment.id, 1)
        self.assertEqual(user1.experimentgroups[1].experiment.id, 1)
        