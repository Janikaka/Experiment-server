import unittest
import transaction

from pyramid import testing
from .models import (
    Experiments,
    Users,
    ExperimentGroups,
    DataItems,
    DatabaseInterface,
    Configurations
    )

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
        self.dbsession = get_tm_session(session_factory, transaction.manager)

    def init_database(self):
        from .models.meta import Base

        Base.metadata.create_all(self.engine)

    def init_databaseData(self):
        self.DBInterface = DatabaseInterface(self.dbsession)
        experimentgroups = []
        experimentgroupNames = ['group A', 'group B', 'group C', 'group D']
        for name in experimentgroupNames:
            experimentgroups.append(self.DBInterface.createExperimentgroup({'name': name}))
        experiment1 = self.DBInterface.createExperiment({'name': 'First experiment', 'experimentgroups':[experimentgroups[0], experimentgroups[1]]})
        experiment2 = self.DBInterface.createExperiment({'name': 'Second experiment', 'experimentgroups':[experimentgroups[2], experimentgroups[3]]})
        user1 = self.DBInterface.createUser({'username': 'First user', 'password': 'First password', 'experimentgroups': [experiment1.experimentgroups[0]]})
        user2 = self.DBInterface.createUser({'username': 'Second user', 'password': 'Second password', 'experimentgroups': [experiment1.experimentgroups[1]]})
        user3 = self.DBInterface.createUser({'username': 'Third user', 'password': 'Third password', 'experimentgroups': [experiment2.experimentgroups[0]]})
        user4 = self.DBInterface.createUser({'username': 'Fourth user', 'password': 'Fourth password', 'experimentgroups': [experiment2.experimentgroups[1]]})
        user5 = self.DBInterface.createUser({'username': 'Fifth user', 'password': 'Fifth password'})
        self.DBInterface.createDataitem({'user': 1, 'value': 10})
        self.DBInterface.createDataitem({'user': 2, 'value': 20})
        self.DBInterface.createDataitem({'user': 3, 'value': 30})
        self.DBInterface.createDataitem({'user': 4, 'value': 40})
        configurations = [{'key': 'key1', 'value': 1, 'experimentgroup': experimentgroups[0]},
        {'key': 'key2', 'value': 2, 'experimentgroup': experimentgroups[1]},
        {'key': 'key3', 'value': 3, 'experimentgroup': experimentgroups[2]}, 
        {'key': 'key4', 'value': 4, 'experimentgroup': experimentgroups[3]}]
        self.DBInterface.createConfiguration(configurations[0])
        self.DBInterface.createConfiguration(configurations[1])
        self.DBInterface.createConfiguration(configurations[2])
        self.DBInterface.createConfiguration(configurations[3])

    def tearDown(self):
        from .models.meta import Base

        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(self.engine)


#---------------------------------------------------------------------------------
#                               DatabaseInterface
#---------------------------------------------------------------------------------

class TestDatabaseInterface(BaseTest):
#TODO: structure this
    def setUp(self):
        super(TestDatabaseInterface, self).setUp()
        self.init_database()
        self.init_databaseData()

    def test_createExperimentgroup(self):
        experimentgroupsFromDB = self.dbsession.query(ExperimentGroups).all()
        users = [
        self.dbsession.query(Users).filter_by(id=1).one(),
        self.dbsession.query(Users).filter_by(id=2).one(),
        self.dbsession.query(Users).filter_by(id=3).one(),
        self.dbsession.query(Users).filter_by(id=4).one()]

        confs = [
        self.dbsession.query(Configurations).filter_by(id=1).one(),
        self.dbsession.query(Configurations).filter_by(id=2).one(),
        self.dbsession.query(Configurations).filter_by(id=3).one(),
        self.dbsession.query(Configurations).filter_by(id=4).one()]

        experiments = [
        self.dbsession.query(Experiments).filter_by(id=1).one(),
        self.dbsession.query(Experiments).filter_by(id=2).one()]

        experimentgroups = [
        {'name':'group A', 'experiment':experiments[0], 'users': [users[0]], 'configuration': confs[0]},
        {'name':'group B', 'experiment':experiments[0], 'users': [users[1]], 'configuration': confs[1]},
        {'name':'group C', 'experiment':experiments[1], 'users': [users[2]], 'configuration': confs[2]},
        {'name':'group D', 'experiment':experiments[1], 'users': [users[3]], 'configuration': confs[3]}]

        for i in range(len(experimentgroupsFromDB)):
            assert experimentgroupsFromDB[i].name == experimentgroups[i]['name']
            assert experimentgroupsFromDB[i].experiment == experimentgroups[i]['experiment']
            assert experimentgroupsFromDB[i].users == experimentgroups[i]['users']
            assert experimentgroupsFromDB[i].configuration == experimentgroups[i]['configuration']


    def test_createExperiment(self):
        experimentsFromDB = self.dbsession.query(Experiments).all()
        
        experiments = [
        {'name':'First experiment', 'experimentgroups':['group A', 'group B']},
        {'name':'Second experiment', 'experimentgroups':['group C', 'group D']}]

        for i in range(len(experimentsFromDB)):
            assert experimentsFromDB[i].name == experiments[i]['name']
            for j in range(len(experimentsFromDB[i].experimentgroups)):
                assert experimentsFromDB[i].experimentgroups[j].name == experiments[i]['experimentgroups'][j]

        

    def test_createUser(self):
        usersFromDB = self.dbsession.query(Users).all()
        users = [
        {'username': 'First user', 'password': 'First password', 
        'experimentgroups': [self.dbsession.query(ExperimentGroups).filter_by(name='group A').one()], 
        'dataitems': [self.dbsession.query(DataItems).filter_by(value=10).one()]},

        {'username': 'Second user', 'password': 'Second password',
        'experimentgroups': [self.dbsession.query(ExperimentGroups).filter_by(name='group B').one()], 
        'dataitems': [self.dbsession.query(DataItems).filter_by(value=20).one()]},

        {'username': 'Third user', 'password': 'Third password',
        'experimentgroups': [self.dbsession.query(ExperimentGroups).filter_by(name='group C').one()], 
        'dataitems': [self.dbsession.query(DataItems).filter_by(value=30).one()]},

        {'username': 'Fourth user', 'password': 'Fourth password', 
        'experimentgroups': [self.dbsession.query(ExperimentGroups).filter_by(name='group D').one()], 
        'dataitems': [self.dbsession.query(DataItems).filter_by(value=40).one()]},

        {'username': 'Fifth user', 'password': 'Fifth password',
        'experimentgroups': [], 
        'dataitems': []}]
        for i in range(len(usersFromDB)):
            for key in users[i]:
                assert getattr(usersFromDB[i], key) == users[i][key]

    def test_createDataitem(self):
        dataitemsFromDB = self.dbsession.query(DataItems).all()
        user1 = self.dbsession.query(Users).filter_by(id=1).one()
        user2 = self.dbsession.query(Users).filter_by(id=2).one()
        user3 = self.dbsession.query(Users).filter_by(id=3).one()
        user4 = self.dbsession.query(Users).filter_by(id=4).one()
        dataitems = [
        {'id':1, 'value': 10, 'user': user1},
        {'id':2, 'value': 20, 'user': user2},
        {'id':3, 'value': 30, 'user': user3},
        {'id':4, 'value': 40, 'user': user4}]

        for i in range(len(dataitemsFromDB)):
            for key in dataitems[i]:
                assert getattr(dataitemsFromDB[i], key) == dataitems[i][key]

    def test_createConfiguration(self):
        confsFromDB = self.dbsession.query(Configurations).all()
        expgroup1 = self.dbsession.query(ExperimentGroups).filter_by(id=1).one()
        expgroup2 = self.dbsession.query(ExperimentGroups).filter_by(id=2).one()
        expgroup3 = self.dbsession.query(ExperimentGroups).filter_by(id=3).one()
        expgroup4 = self.dbsession.query(ExperimentGroups).filter_by(id=4).one()
        confs = [
        {'id': 1, 'key': 'key1', 'value': 1, 'experimentgroup': expgroup1},
        {'id': 2, 'key': 'key2', 'value': 2, 'experimentgroup': expgroup2},
        {'id': 3, 'key': 'key3', 'value': 3, 'experimentgroup': expgroup3},
        {'id': 4, 'key': 'key4', 'value': 4, 'experimentgroup': expgroup4}]

        for i in range(len(confsFromDB)):
            for keyy in confs[i]:
                assert getattr(confsFromDB[i], keyy) == confs[i][keyy]


    def test_deleteExperiment(self):
        self.DBInterface.deleteExperiment(1) #Delete experiment 'First experiment'
        experimentsFromDB = self.dbsession.query(Experiments).all()
        assert len(experimentsFromDB) == 1
        assert experimentsFromDB[0].id == 2
        experimentgroupsFromDB = self.dbsession.query(ExperimentGroups).all()
        names = ['group C', 'group D']
        for i in range(len(experimentgroupsFromDB)):
            assert experimentgroupsFromDB[i].name == names[i]
        user1 = self.dbsession.query(Users).filter_by(id=1).one()
        user2 = self.dbsession.query(Users).filter_by(id=2).one()
        assert user1.experimentgroups == []
        assert user2.experimentgroups == []
        
    def test_deleteUser(self):
        self.DBInterface.deleteUser(1)
        self.DBInterface.deleteUser(3)

        usersFromDB = self.dbsession.query(Users).all()
        dataitemsFromDB = self.dbsession.query(DataItems).all()
        experimentgroupsFromDB = self.dbsession.query(ExperimentGroups).all()

        user2 = self.dbsession.query(Users).filter_by(id=2).one()
        user4 = self.dbsession.query(Users).filter_by(id=4).one()
        user5 = self.dbsession.query(Users).filter_by(id=5).one()

        dataitem2 = self.dbsession.query(DataItems).filter_by(id=2).one()
        dataitem4 = self.dbsession.query(DataItems).filter_by(id=4).one()

        users = [user2, user4, user5]
        dataitems = [dataitem2, dataitem4]

        assert usersFromDB == users
        assert dataitemsFromDB == dataitems
        assert len(experimentgroupsFromDB) == 4

    def test_deleteExperimentgroup(self):
        self.DBInterface.deleteExperimentgroup(1) #group A
        self.DBInterface.deleteExperimentgroup(4) #group D

        experimentgroupsFromDB = self.dbsession.query(ExperimentGroups).all()

        expgroup2 = self.dbsession.query(ExperimentGroups).filter_by(id=2).one()
        expgroup3 = self.dbsession.query(ExperimentGroups).filter_by(id=3).one()
        experimentgroups = [expgroup2, expgroup3]

        user1 = self.dbsession.query(Users).filter_by(id=1).one()
        user4 = self.dbsession.query(Users).filter_by(id=4).one()

        assert experimentgroupsFromDB == experimentgroups
        assert user1.experimentgroups == []
        assert user4.experimentgroups == []

    def test_getUsersInExperiment(self):
        users1 = self.DBInterface.getUsersInExperiment(1)
        users2 = self.DBInterface.getUsersInExperiment(2)
        user1 = self.dbsession.query(Users).filter_by(id=1).one()
        user2 = self.dbsession.query(Users).filter_by(id=2).one()
        user3 = self.dbsession.query(Users).filter_by(id=3).one()
        user4 = self.dbsession.query(Users).filter_by(id=4).one()
        users1FromDB = [user1, user2]
        users2FromDB = [user3, user4]

        assert users1 == users1FromDB
        assert users2 == users2FromDB

    def test_getExperimentsForUser(self):
        experiments1 = self.DBInterface.getExperimentsForUser(1)
        experiments2 = self.DBInterface.getExperimentsForUser(2)
        experiments3 = self.DBInterface.getExperimentsForUser(3)
        experiments4 = self.DBInterface.getExperimentsForUser(4)
        experiments5 = self.DBInterface.getExperimentsForUser(5)
        
        experiment1 = self.dbsession.query(Experiments).filter_by(id=1).one()
        experiment2 = self.dbsession.query(Experiments).filter_by(id=2).one()

        assert experiments1 == [experiment1]
        assert experiments2 == [experiment1]
        assert experiments3 == [experiment2]
        assert experiments4 == [experiment2]
        assert experiments5 == []

    

    






