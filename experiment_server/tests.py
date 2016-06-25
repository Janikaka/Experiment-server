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
        self.DBInterface.createExperiment({'name': 'First experiment', 'experimentgroupNames':['group A', 'group B']})
        self.DBInterface.createExperiment({'name': 'Second experiment', 'experimentgroupNames':['group C', 'group D']})
        self.DBInterface.createUser({'username': 'First user', 'password': 'First password'})
        self.DBInterface.createUser({'username': 'Second user', 'password': 'Second password'})
        self.DBInterface.createUser({'username': 'Third user', 'password': 'Third password'})
        self.DBInterface.createUser({'username': 'Fourth user', 'password': 'Fourth password'})


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
    




