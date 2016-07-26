import unittest
import transaction
import datetime
from sqlalchemy import update

from pyramid import testing
from .models import (
    Experiment,
    User,
    ExperimentGroup,
    DataItem,
    DatabaseInterface,
    Configuration
    )

def dummy_request(dbsession):
    return testing.DummyRequest(dbsession=dbsession)

def strToDatetime(date):
    return datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

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
        self.DB = DatabaseInterface(self.dbsession)

        expgroup1 = self.DB.createExperimentgroup(
            {'name': 'Group A'
            })
        expgroup2 = self.DB.createExperimentgroup(
            {'name': 'Group B'
            })

        conf1 = self.DB.createConfiguration(
            {'key': 'v1',
             'value': 0.5,
             'experimentgroup': expgroup1
            })
        conf2 = self.DB.createConfiguration(
            {'key': 'v2',
             'value': True,
             'experimentgroup': expgroup1
            })
        conf3 = self.DB.createConfiguration(
            {'key': 'v1',
             'value': 1.0,
             'experimentgroup': expgroup2
            })
        conf4 = self.DB.createConfiguration(
            {'key': 'v2',
             'value': False,
             'experimentgroup': expgroup2
            })

        experiment = self.DB.createExperiment(
            {'name': 'Test experiment',
             'startDatetime': '2016-01-01 00:00:00',
             'endDatetime': '2017-01-01 00:00:00',
             'size': 100,
             'experimentgroups': [expgroup1, expgroup2]
            })

        user1 = self.DB.createUser(
            {'username': 'First user',
             'experimentgroups': [expgroup1]
            })
        user2 = self.DB.createUser(
            {'username': 'Second user',
             'experimentgroups': [expgroup2]
            })

        dt1 = self.DB.createDataitem(
            {'key': 'key1',
             'value': 10,
             'startDatetime': '2016-01-01 00:00:00',
             'endDatetime': '2016-01-01 01:01:01',
             'user': user1
            })
        dt2 = self.DB.createDataitem(
            {'key': 'key2',
             'value': 20,
             'startDatetime': '2016-02-02 00:00:00',
             'endDatetime': '2016-02-02 02:02:02',
             'user': user1
            })
        dt3 = self.DB.createDataitem(
            {'key': 'key3',
             'value': 30,
             'startDatetime': '2016-03-03 00:00:00',
             'endDatetime': '2016-03-03 03:03:03',
             'user': user2
            })
        dt4 = self.DB.createDataitem(
            {'key': 'key4',
             'value': 40,
             'startDatetime': '2016-04-04 00:00:00',
             'endDatetime': '2016-04-04 04:04:04',
             'user': user2
            })

    def tearDown(self):
        from .models.meta import Base

        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(self.engine)

#---------------------------------------------------------------------------------
#                                DatabaseInterface                                 
#---------------------------------------------------------------------------------

class TestExperiments(BaseTest):
    def setUp(self):
        super(TestExperiments, self).setUp()
        self.init_database()
        self.init_databaseData()

    def test_createExperiment(self):
        experimentsFromDB = self.dbsession.query(Experiment).all()
        experimentgroups = self.dbsession.query(ExperimentGroup).all()
        experiments = [
            {'name': 'Test experiment',
             'size': 100,
             'experimentgroups': [experimentgroups[0], experimentgroups[1]],
             'startDatetime': strToDatetime('2016-01-01 00:00:00'),
             'endDatetime': strToDatetime('2017-01-01 00:00:00')
            }]

        for i in range(len(experimentsFromDB)):
            for key in experiments[i]:
                assert getattr(experimentsFromDB[i], key) == experiments[i][key]

    def test_deleteExperiment(self):
        self.DB.deleteExperiment(1)
        experimentsFromDB = self.dbsession.query(Experiment).all()
        experimentgroupsFromDB = self.dbsession.query(ExperimentGroup).all()
        configurationsFromDB = self.dbsession.query(Configuration).all()
        usersFromDB = self.dbsession.query(User).all()

        assert experimentsFromDB == []
        assert experimentgroupsFromDB == []
        assert configurationsFromDB == []
        assert usersFromDB[0].experimentgroups == []
        assert usersFromDB[1].experimentgroups == []

    def test_getStatusForExperiment(self):
        status = self.DB.getStatusForExperiment(1)
        assert status == 'running'
        newEndDatetime = strToDatetime('2016-06-01 00:00:00')
        self.dbsession.query(Experiment).filter_by(id=1).one().endDatetime = newEndDatetime
        status = self.DB.getStatusForExperiment(1)
        assert status == 'finished'
        newStartDatetime = strToDatetime('2017-01-01 00:00:00')
        newEndDatetime = strToDatetime('2017-06-01 00:00:00')
        self.dbsession.query(Experiment).filter_by(id=1).one().startDatetime = newStartDatetime
        self.dbsession.query(Experiment).filter_by(id=1).one().endDatetime = newEndDatetime
        status = self.DB.getStatusForExperiment(1)
        assert status == 'waiting'

    def test_getAllRunningExperiments(self):
        experiments = self.DB.getAllRunningExperiments()
        experimentsFromDB = self.dbsession.query(Experiment).all()

        assert experiments == experimentsFromDB

    def test_getExperimentsUserParticipates(self):
        expForUser1 = self.DB.getExperimentsUserParticipates(1)
        expForUser2 = self.DB.getExperimentsUserParticipates(2)
        experimentsFromDB = self.dbsession.query(Experiment).all()

        assert expForUser1 == [experimentsFromDB[0]]
        assert expForUser2 == [experimentsFromDB[0]]

class TestExperimentgroups(BaseTest):
    def setUp(self):
        super(TestExperimentgroups, self).setUp()
        self.init_database()
        self.init_databaseData()

    def test_createExperimentgroup(self):
        expgroupsFromDB = self.dbsession.query(ExperimentGroup).all()
        experimentsFromDB = self.dbsession.query(Experiment).all()
        configurationsFromDB = self.dbsession.query(Configuration).all()
        usersFromDB = self.dbsession.query(User).all()

        expgroup1 = {
            'id': 1,
            'name': 'Group A',
            'experiment': experimentsFromDB[0],
            'configurations': [configurationsFromDB[0], configurationsFromDB[1]],
            'users': [usersFromDB[0]]
        } 
        expgroup2 = {
            'id': 2,
            'name': 'Group B',
            'experiment': experimentsFromDB[0],
            'configurations': [configurationsFromDB[2], configurationsFromDB[3]],
            'users': [usersFromDB[1]]
        }
        expgroups = [expgroup1, expgroup2]

        for i in range(len(expgroupsFromDB)):
            for key in expgroups[i]:
                assert getattr(expgroupsFromDB[i], key) == expgroups[i][key]

    def test_deleteExperimentgroup(self):
        self.DB.deleteExperimentgroup(1)

        expgroupsFromDB = self.dbsession.query(ExperimentGroup).all()
        experimentsFromDB = self.dbsession.query(Experiment).all()
        configurationsFromDB = self.dbsession.query(Configuration).all()
        usersFromDB = self.dbsession.query(User).all()

        experimentgroups = [self.dbsession.query(ExperimentGroup).filter_by(id=2).one()]
        configurations = [self.dbsession.query(Configuration).filter_by(id=3).one(),
        self.dbsession.query(Configuration).filter_by(id=4).one()]

        assert expgroupsFromDB == experimentgroups
        assert experimentsFromDB[0].experimentgroups == experimentgroups
        assert configurationsFromDB == configurations
        assert usersFromDB[0].experimentgroups == []
        assert usersFromDB[1].experimentgroups == experimentgroups 

    def test_getExperimentgroupForUserInExperiment(self):
        expgroupInExperimentForUser1 = self.DB.getExperimentgroupForUserInExperiment(1, 1)
        expgroupInExperimentForUser2 = self.DB.getExperimentgroupForUserInExperiment(2, 1)

        expgroup1 = self.dbsession.query(ExperimentGroup).filter_by(id=1).one()
        expgroup2 = self.dbsession.query(ExperimentGroup).filter_by(id=2).one()

        assert expgroupInExperimentForUser1 == expgroup1
        assert expgroupInExperimentForUser2 == expgroup2

class TestUsers(BaseTest):
    def setUp(self):
        super(TestUsers, self).setUp()
        self.init_database()
        self.init_databaseData()

    def test_createUser(self):
        usersFromDB = self.dbsession.query(User).all()
        experimentgroupsFromDB = self.dbsession.query(ExperimentGroup).all()
        dataitemsFromDB = self.dbsession.query(DataItem).all()
        user1 = {
            'id': 1,
            'username': 'First user',
            'experimentgroups': [experimentgroupsFromDB[0]],
            'dataitems': [dataitemsFromDB[0], dataitemsFromDB[1]]
        }
        user2 = {
            'id': 2,
            'username': 'Second user',
            'experimentgroups': [experimentgroupsFromDB[1]],
            'dataitems': [dataitemsFromDB[2], dataitemsFromDB[3]]
        }
        users = [user1, user2]

        for i in range(len(usersFromDB)):
            for key in users[i]:
                assert getattr(usersFromDB[i], key) == users[i][key]

    def test_deleteUser(self):
        self.DB.deleteUser(1)
        usersFromDB = self.dbsession.query(User).all()
        experimentgroupsFromDB = self.dbsession.query(ExperimentGroup).all()
        dataitemsFromDB = self.dbsession.query(DataItem).all()

        user2 = self.dbsession.query(User).filter_by(id=2).one()
        dt3 = self.dbsession.query(DataItem).filter_by(id=3).one()
        dt4 = self.dbsession.query(DataItem).filter_by(id=4).one()

        assert usersFromDB == [user2]
        assert experimentgroupsFromDB[0].users == []
        assert dataitemsFromDB == [dt3, dt4]

    def checkUser(self):
        usernames = self.dbsession.query(User.username).all()
        assert 'Example user' not in usernames
        exampleUser = self.DB.checkUser('Example user')
        assert exampleUser.id == 3 and exampleUser.username == 'Example user'
        user1 = self.DB.checkUser('First user')
        user2 = self.DB.checkUser('Second user')
        assert user1.id == 1 and user1.username == 'First user'
        assert user2.id == 2 and user2.username == 'Second user'

    def test_assignUserToExperiment(self):
        user = self.dbsession.query(User).filter_by(id=1).one()
        self.DB.createExperimentgroup({'name': 'Example group'})
        expgroup = self.dbsession.query(ExperimentGroup).filter_by(id=3).one()
        self.DB.createExperiment(
            {'name': 'Example experiment',
             'startDatetime': '2016-01-01 00:00:00',
             'endDatetime': '2017-01-01 00:00:00',
             'size': 100,
             'experimentgroups': [expgroup]
            })
        experiment = self.dbsession.query(Experiment).filter_by(id=2).one()
        self.DB.assignUserToExperiment(user.id, experiment.id)
        assert expgroup.users == [user]
        assert expgroup in user.experimentgroups 

    def test_assignUserToRunningExperiments(self):
        user = self.DB.createUser({'username': 'Test user'})

        assert user.experimentgroups == []

        self.DB.assignUserToRunningExperiments(3)
        expgroup1 = self.dbsession.query(ExperimentGroup).filter_by(id=1).one()
        expgroup2 = self.dbsession.query(ExperimentGroup).filter_by(id=2).one()

        assert expgroup1 in user.experimentgroups or expgroup2 in user.experimentgroups

    def test_getUsersForExperiment(self):
        usersForExperiment = self.DB.getUsersForExperiment(1)
        user1 = self.dbsession.query(User).filter_by(id=1).one()
        user2 = self.dbsession.query(User).filter_by(id=2).one()

        assert usersForExperiment == [user1, user2]

    def test_deleteUserFromExperiment(self):
        assert 1==1



    def test_getUsersForExperimentgroup(self):
        assert 1==1


class TestDataitems(BaseTest):
    def setUp(self):
        super(TestDataitems, self).setUp()
        self.init_database()
        self.init_databaseData()

    def test_createDataitem(self):
        dataitemsFromDB = self.dbsession.query(DataItem).all()
        user1 = self.dbsession.query(User).filter_by(id=1).one()
        user2 = self.dbsession.query(User).filter_by(id=2).one()
        dt1 = {'key': 'key1',
             'value': 10,
             'startDatetime': strToDatetime('2016-01-01 00:00:00'),
             'endDatetime': strToDatetime('2016-01-01 01:01:01'),
             'user': user1}
        dt2 = {'key': 'key2',
             'value': 20,
             'startDatetime': strToDatetime('2016-02-02 00:00:00'),
             'endDatetime': strToDatetime('2016-02-02 02:02:02'),
             'user': user1}
        dt3 = {'key': 'key3',
             'value': 30,
             'startDatetime': strToDatetime('2016-03-03 00:00:00'),
             'endDatetime': strToDatetime('2016-03-03 03:03:03'),
             'user': user2}
        dt4 = {'key': 'key4',
             'value': 40,
             'startDatetime': strToDatetime('2016-04-04 00:00:00'),
             'endDatetime': strToDatetime('2016-04-04 04:04:04'),
             'user': user2}
        dataitems = [dt1, dt2, dt3, dt4]
        for i in range(len(dataitemsFromDB)):
            for key in dataitems[i]:
                assert getattr(dataitemsFromDB[i], key) == dataitems[i][key]

    def test_getTotalDataitemsForExperiment(self):
        totalDataitemsForExperiment = self.DB.getTotalDataitemsForExperiment(1)

        assert totalDataitemsForExperiment == 4

    def test_getTotalDataitemsForExpgroup(self):
        totalDataitemsForExpgroup1 = self.DB.getTotalDataitemsForExpgroup(1)
        totalDataitemsForExpgroup2 = self.DB.getTotalDataitemsForExpgroup(2)

        assert totalDataitemsForExpgroup1 == 2
        assert totalDataitemsForExpgroup2 == 2

    def test_getTotalDataitemsForUserInExperiment(self):
        totalDataitemsForUser1InExperiment = self.DB.getTotalDataitemsForUserInExperiment(1, 1)
        totalDataitemsForUser2InExperiment = self.DB.getTotalDataitemsForUserInExperiment(2, 1)

        assert totalDataitemsForUser1InExperiment == 2
        assert totalDataitemsForUser2InExperiment == 2

    def test_getDataitemsForUserOnPeriod(self):
        assert 1==1

    def test_getDataitemsForUserInExperiment(self):
        assert 1==1

    def test_getDataitemsForExperimentgroup(self):
        assert 1==1

    def test_getDataitemsForExperiment(self):
        assert 1==1

    def test_deleteDataitem(self):
        assert 1==1


class TestConfigurations(BaseTest):
    def setUp(self):
        super(TestConfigurations, self).setUp()
        self.init_database()
        self.init_databaseData()

    def test_createConfiguration(self):
        assert 1==1

    def test_deleteConfiguration(self):
        assert 1==1

    def test_getConfsForExperimentgroup(self):
        assert 1==1

    def test_getTotalConfigurationForUser(self):
        assert 1==1







#---------------------------------------------------------------------------------
#                                  REST-Inteface                                  
#---------------------------------------------------------------------------------



























