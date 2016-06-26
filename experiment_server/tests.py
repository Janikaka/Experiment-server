import unittest
import transaction

from pyramid import testing
from .models import (
    Experiments,
    Users,
    ExperimentGroups,
    DataItems,
    DatabaseInterface
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
        experiment1 = self.DBInterface.createExperiment({'name': 'First experiment', 'experimentgroupNames':['group A', 'group B']})
        experiment2 = self.DBInterface.createExperiment({'name': 'Second experiment', 'experimentgroupNames':['group C', 'group D']})
        user1 = self.DBInterface.createUser({'username': 'First user', 'password': 'First password', 'experimentgroups': [experiment1.experimentgroups[0]]})
        user2 = self.DBInterface.createUser({'username': 'Second user', 'password': 'Second password', 'experimentgroups': [experiment1.experimentgroups[1]]})
        user3 = self.DBInterface.createUser({'username': 'Third user', 'password': 'Third password', 'experimentgroups': [experiment2.experimentgroups[0]]})
        user4 = self.DBInterface.createUser({'username': 'Fourth user', 'password': 'Fourth password', 'experimentgroups': [experiment2.experimentgroups[1]]})
        self.DBInterface.createDataitem({'user': 1, 'value': 10})
        self.DBInterface.createDataitem({'user': 2, 'value': 20})
        self.DBInterface.createDataitem({'user': 3, 'value': 30})
        self.DBInterface.createDataitem({'user': 4, 'value': 40})

    def tearDown(self):
        from .models.meta import Base

        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(self.engine)


#---------------------------------------------------------------------------------
#                               DatabaseInterface
#---------------------------------------------------------------------------------

from .models import DatabaseInterface

class TestDatabaseInterface(BaseTest):

    def setUp(self):
        super(TestDatabaseInterface, self).setUp()
        self.init_database()
        self.init_databaseData()

    def test_createExperiment(self):
        experimentsFromDB = self.dbsession.query(Experiments).all()
        experiments = [
        {'name':'First experiment', 'experimentgroups':['group A', 'group B']},
        {'name':'Second experiment', 'experimentgroups':['group C', 'group D']}]
        for i in range(len(experimentsFromDB)):
            assert experimentsFromDB[i].name == experiments[i]['name']
            for j in range(len(experimentsFromDB[i].experimentgroups)):
                assert experimentsFromDB[i].experimentgroups[j].name == experiments[i]['experimentgroups'][j]

    def test_deleteExperiment(self):
        self.DBInterface.deleteExperiment(1) #Delete experiment 'First experiment'
        experimentsFromDB = self.dbsession.query(Experiments).all()
        assert len(experimentsFromDB) == 1
        assert experimentsFromDB[0].id == 2
        experimentgroupsFromDB = self.dbsession.query(ExperimentGroups).all()
        names = ['group C', 'group D']
        for i in range(len(experimentgroupsFromDB)):
            assert experimentgroupsFromDB[i].name == names[i]
        
    def test_createUser(self):
        usersFromDB = self.dbsession.query(Users).all()
        users = [
        {'username': 'First user', 'password': 'First password'},
        {'username': 'Second user', 'password': 'Second password'},
        {'username': 'Third user', 'password': 'Third password'},
        {'username': 'Fourth user', 'password': 'Fourth password'}]
        for i in range(len(usersFromDB)):
            assert usersFromDB[i].username == users[i]['username']
            assert usersFromDB[i].password == users[i]['password']

    def test_getUsersInExperiment(self):
        users1 = self.DBInterface.getUsersInExperiment(1)
        users2 = self.DBInterface.getUsersInExperiment(2)
        users1FromDB = [self.dbsession.query(Users).filter_by(id=1).one(), self.dbsession.query(Users).filter_by(id=2).one()]
        users2FromDB = [self.dbsession.query(Users).filter_by(id=3).one(), self.dbsession.query(Users).filter_by(id=4).one()]

        assert users1 == users1FromDB
        assert users2 == users2FromDB

    def test_getExperimentsForUser(self):
        experiments1 = self.DBInterface.getExperimentsForUser(1)
        experiments2 = self.DBInterface.getExperimentsForUser(2)
        experiments3 = self.DBInterface.getExperimentsForUser(3)
        experiments4 = self.DBInterface.getExperimentsForUser(4)
        
        experiment1 = self.dbsession.query(Experiments).filter_by(id=1).one()
        experiment2 = self.dbsession.query(Experiments).filter_by(id=2).one()

        assert experiments1 == [experiment1]
        assert experiments2 == [experiment1]
        assert experiments3 == [experiment2]
        assert experiments4 == [experiment2]


    def test_createDataitem(self):
        dataitem1 = self.dbsession.query(DataItems).filter_by(id=1).one()
        dataitem2 = self.dbsession.query(DataItems).filter_by(id=2).one()
        dataitem3 = self.dbsession.query(DataItems).filter_by(id=3).one()
        dataitem4 = self.dbsession.query(DataItems).filter_by(id=4).one()
        user1 = self.dbsession.query(Users).filter_by(id=1).one()
        user2 = self.dbsession.query(Users).filter_by(id=2).one()
        user3 = self.dbsession.query(Users).filter_by(id=3).one()
        user4 = self.dbsession.query(Users).filter_by(id=4).one()

        assert len(self.dbsession.query(DataItems).all()) == 4
        assert dataitem1.value == 10 and dataitem1.user == user1 and dataitem1.id == 1
        assert dataitem2.value == 20 and dataitem2.user == user2 and dataitem2.id == 2
        assert dataitem3.value == 30 and dataitem3.user == user3 and dataitem3.id == 3
        assert dataitem4.value == 40 and dataitem4.user == user4 and dataitem4.id == 4

    def test_deleteUser(self):
        self.DBInterface.deleteUser(1)
        self.DBInterface.deleteUser(3)

        usersFromDB = self.dbsession.query(Users).all()
        dataitemsFromDB = self.dbsession.query(DataItems).all()
        experimentgroupsFromDB = self.dbsession.query(ExperimentGroups).all()

        users = [self.dbsession.query(Users).filter_by(id=2).one(), self.dbsession.query(Users).filter_by(id=4).one()]
        dataitems = [self.dbsession.query(DataItems).filter_by(id=2).one(), self.dbsession.query(DataItems).filter_by(id=4).one()]

        assert usersFromDB == users
        assert dataitemsFromDB == dataitems
        assert len(experimentgroupsFromDB) == 4







