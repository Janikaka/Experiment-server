import unittest
import pytest
import transaction

from pyramid import testing
from .models import (
    Experiments,
    Users,
    ExperimentGroups,
    DataItems
    )

def dummy_request(dbsession):
    return testing.DummyRequest(dbsession=dbsession)

@pytest.fixture(scope="module")
def create_Experiment(request):
    def create(session, name, experimentgroups):
        experiment = Experiments(name=name)
        if experimentgroups != None:
            for experimentgroup in experimentgroups:
                experiment.experimentgroups.append(experimentgroup)
            session.add(experiment)
        return experiment
    return create

def create_ExperimentGroup(session, name, experiment, users):
    experimentGroup = ExperimentGroups(name=name)
    if experiment != None:
        experiment.experimentgroups.append(experimentGroup)
    if users != None:
        for user in users:
            experimentGroup.users.append(user)
    session.add(experimentGroup)
    return experimentGroup

def create_User(session, username, password):
    user = Users(username=username, password=password)
    session.add(user)
    return user

def create_DataItem(session, value, user):
    dataItem = DataItems(value=value)
    if user != None:
        dataItem.user = user
    session.add(dataItem)
    return dataItem

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

        experimentGroup = create_ExperimentGroup(self.session, 'expgroupA', None, None)
        create_Experiment(self.session, 'first experiment', [experimentGroup])
        create_Experiment(self.session, 'second experiment', None)

    def test_add_experiments(self):

        exp1 = self.session.query(Experiments).filter_by(name='first experiment').one()
        exp2 = self.session.query(Experiments).filter_by(name='second experiment').one()

        self.assertEqual(exp1.name, 'first experiment')
        self.assertEqual(exp1.id, 1)
        self.assertEqual(exp2.name, 'second experiment')
        self.assertEqual(exp2.id, 2)
        self.assertEqual(len(self.session.query(Experiments).all()), 2)
        

    def test_data_from_added_experiments(self):
        exp1 = self.session.query(Experiments).filter_by(name='first experiment').one()
        exp2 = self.session.query(Experiments).filter_by(name='second experiment').one()
        expgroup = self.session.query(ExperimentGroups).filter_by(name='expgroupA').one()
        
        self.assertEqual(exp1.experimentgroups, [expgroup])
        self.assertEqual(exp1.experimentgroups[0].experiment, exp1)
        self.assertEqual(len(exp2.experimentgroups), 0)

class TestExperimentGroups(BaseTest):

    def setUp(self):
        super(TestExperimentGroups, self).setUp()
        self.init_database()

        experiment = create_Experiment(self.session, 'first experiment', None)
        user1 = create_User(self.session, 'first user', 'first password')
        user2 = create_User(self.session, 'second user', 'second password')
        create_ExperimentGroup(self.session, 'expgroupA', experiment, [user1])
        create_ExperimentGroup(self.session, 'expgroupB', experiment, [user2])


    def test_add_experimentGroups(self):
        expGroup1 = self.session.query(ExperimentGroups).filter_by(id=1).one()
        expGroup2 = self.session.query(ExperimentGroups).filter_by(id=2).one()

        self.assertEqual(expGroup1.name, 'expgroupA')
        self.assertEqual(expGroup2.name, 'expgroupB')

        self.assertEqual(len(self.session.query(ExperimentGroups).all()), 2)
        
    def test_data_from_added_experimentGroups(self):
        expGroup1 = self.session.query(ExperimentGroups).filter_by(id=1).one()
        expGroup2 = self.session.query(ExperimentGroups).filter_by(id=2).one()
        user1 = self.session.query(Users).filter_by(username='first user').one()
        user2 = self.session.query(Users).filter_by(username='second user').one()
        experiment = self.session.query(Experiments).filter_by(name='first experiment').one()

        self.assertEqual(expGroup1.experiment, experiment)
        self.assertEqual(expGroup2.experiment, experiment)
        self.assertEqual(expGroup1.users, [user1])
        self.assertEqual(expGroup2.users, [user2])


class TestUsers(BaseTest):

    def setUp(self):
        super(TestUsers, self).setUp()
        self.init_database()

        user1 = create_User(self.session, 'first user', 'first password')
        user2 = create_User(self.session, 'second user', 'second password')

        dataItem1 = create_DataItem(self.session, 10, user1)
        dataItem2 = create_DataItem(self.session, 20, user2)

        experiment = create_Experiment(self.session, 'first experiment', None)
        experimentGroup1 = create_ExperimentGroup(self.session, 'expgroupA', experiment, [user1])
        experimentGroup2 = create_ExperimentGroup(self.session, 'expgroupB', experiment, [user2])


    def test_add_users(self):
        user1 = self.session.query(Users).filter_by(username='first user').one()
        user2 = self.session.query(Users).filter_by(username='second user').one()

        self.assertEqual(user1.username, 'first user')
        self.assertEqual(user1.id, 1)
        self.assertEqual(user2.username, 'second user')
        self.assertEqual(user2.id, 2)
        self.assertEqual(len(self.session.query(Users).all()), 2)
    
    def test_data_from_added_users(self):
        user1 = self.session.query(Users).filter_by(username='first user').one()
        user2 = self.session.query(Users).filter_by(username='second user').one()
        dataitem1 = self.session.query(DataItems).filter_by(id=1).one()
        dataitem2 = self.session.query(DataItems).filter_by(id=2).one()
        experimentGroup1 = self.session.query(ExperimentGroups).filter_by(id=1).one()
        experimentGroup2 = self.session.query(ExperimentGroups).filter_by(id=2).one()

        self.assertEqual(user1.dataitems, [dataitem1])
        self.assertEqual(user2.dataitems, [dataitem2])
        self.assertEqual(user1.experimentgroups, [experimentGroup1])
        self.assertEqual(user2.experimentgroups, [experimentGroup2])


class TestDataItems(BaseTest):

    def setUp(self):
        super(TestDataItems, self).setUp()
        self.init_database()

        user1 = create_User(self.session, 'first user', 'first password')
        user2 = create_User(self.session, 'second user', 'second password')

        dataItem1 = create_DataItem(self.session, 10, user1)
        dataItem2 = create_DataItem(self.session, 20, user2)

    def test_add_DataItems(self):
        
        dataItem1 = self.session.query(DataItems).filter_by(id=1).one()
        dataItem2 = self.session.query(DataItems).filter_by(id=2).one()

        self.assertEqual(len(self.session.query(DataItems).all()), 2)


    def test_data_from_added_dataItems(self):

        dataItem1 = self.session.query(DataItems).filter_by(id=1).one()
        dataItem2 = self.session.query(DataItems).filter_by(id=2).one()

        user1 = self.session.query(Users).filter_by(id=1).one()
        user2 = self.session.query(Users).filter_by(id=2).one()

        self.assertEqual(dataItem1.user, user1);
        self.assertEqual(dataItem2.user, user2);

        self.assertEqual(dataItem1.value, 10);
        self.assertEqual(dataItem2.value, 20);

        self.assertEqual(user1.dataitems, [dataItem1])
        self.assertEqual(user2.dataitems, [dataItem2])

#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------

def create_user_if_does_not_exists(session, user):
    if len(session.query(Users).all()) == 0:
            session.add(user)

class Test_user_opens_app(BaseTest):

    def setUp(self):
        super(Test_user_opens_app, self).setUp()
        self.init_database()

        self.user = Users(username='test user', password='test password')

    def test_user_does_not_exists(self):

        self.assertEqual(len(self.session.query(Users).all()), 0)

    def test_create_user_if_does_not_exists(self):
        self.assertEqual(len(self.session.query(Users).all()), 0)
        create_user_if_does_not_exists(self.session, self.user)
        self.assertEqual(len(self.session.query(Users).all()), 1)

def get_experiments_in_which_user_participates(session, user):
    experiments = []
    for experiment in session.query(Experiments).all():
        for experimentgroup in experiment.experimentgroups:
            if user in experimentgroup.users:
                experiments.append(experiment)
    return experiments

def get_experimentgroups_in_which_user_participates(session, user):
    experimentgroups = []
    for experiment in session.query(Experiments).all():
        for experimentgroup in experiment.experimentgroups:
            if user in experimentgroup.users:
                experimentgroups.append(experimentgroup)
    return experimentgroups

class Test_get_experiments_and_groups_in_which_user_participates(BaseTest):

    def setUp(self):
        super(Test_get_experiments_and_groups_in_which_user_participates, self).setUp()
        self.init_database()

        self.user = Users(username='test user', password='test password')
        self.session.add(self.user)
        self.experiment1 = Experiments(name='first test experiment')
        self.session.add(self.experiment1)
        self.experiment2 = Experiments(name='second test experiment')
        self.session.add(self.experiment2)

        self.exp1group1 = ExperimentGroups(name='experiment 1 group A', experiment=self.experiment1)
        self.exp1group1.users.append(self.user)
        self.exp1group2 = ExperimentGroups(name='experiment 1 group B', experiment=self.experiment1)
        self.session.add(self.exp1group1)
        self.session.add(self.exp1group2)

        self.exp2group1 = ExperimentGroups(name='experiment 2 group A', experiment=self.experiment2)
        self.exp2group2 = ExperimentGroups(name='experiment 2 group B', experiment=self.experiment2)
        self.exp2group2.users.append(self.user)
        self.session.add(self.exp2group1)
        self.session.add(self.exp2group2)

    def test_get_experiments(self):
        self.assertEqual(len(get_experiments_in_which_user_participates(self.session, self.user)), 2)
        self.assertEqual(get_experiments_in_which_user_participates(self.session, self.user), [self.experiment1, self.experiment2])

    def test_get_experimentgroups(self):
        self.assertEqual(len(get_experimentgroups_in_which_user_participates(self.session, self.user)), 2)
        self.assertEqual(get_experimentgroups_in_which_user_participates(self.session, self.user), [self.exp1group1, self.exp2group2])

def get_experiments_in_which_user_does_not_participate(session, user):
    experiments = []
    for experiment in session.query(Experiments).all():
        participate = False
        for experimentgroup in experiment.experimentgroups:
            if user in experimentgroup.users:
                participate = True
        if participate == False:
            experiments.append(experiment)
    return experiments

def assign_user_to_experiment(experiment, user):
    import random
    experimentgroup = experiment.experimentgroups[random.randint(0, len(experiment.experimentgroups)-1)]
    return experimentgroup

class Test_get_experiments_in_which_user_does_not_participate_and_assign_user(BaseTest):

    def setUp(self):
        super(Test_get_experiments_in_which_user_does_not_participate_and_assign_user, self).setUp()
        self.init_database()

        self.user = Users(username='test user', password='test password')
        self.session.add(self.user)
        self.experiment1 = Experiments(name='first test experiment')
        self.session.add(self.experiment1)
        self.experiment2 = Experiments(name='second test experiment')
        self.session.add(self.experiment2)

        self.exp1group1 = ExperimentGroups(name='experiment 1 group A', experiment=self.experiment1)
        self.exp1group1.users.append(self.user)
        self.exp1group2 = ExperimentGroups(name='experiment 1 group B', experiment=self.experiment1)
        self.session.add(self.exp1group1)
        self.session.add(self.exp1group2)

        self.exp2group1 = ExperimentGroups(name='experiment 2 group A', experiment=self.experiment2)
        self.exp2group2 = ExperimentGroups(name='experiment 2 group B', experiment=self.experiment2)
        self.session.add(self.exp2group1)
        self.session.add(self.exp2group2)

    def test_get_experiments(self):
        self.assertEqual(len(get_experiments_in_which_user_does_not_participate(self.session, self.user)), 1)
        self.assertEqual(get_experiments_in_which_user_does_not_participate(self.session, self.user), [self.experiment2])

    def test_assign_user_to_experiments(self):
        experiments = get_experiments_in_which_user_does_not_participate(self.session, self.user)
        experimentgroups = []

        for experiment in experiments:
            experimentgroup = assign_user_to_experiment(experiment, self.user)
            experimentgroup.users.append(self.user)
            experimentgroups.append(experimentgroup)

        for experimentgroup in experimentgroups:
            self.assertTrue(self.user in experimentgroup.users)