import datetime
from .base_test import BaseTest
from ..models import (Experiment, User, DataItem, ExperimentGroup)
from experiment_server.views.users import Users


# ---------------------------------------------------------------------------------
#                                DatabaseInterface
# ---------------------------------------------------------------------------------

class TestUsers(BaseTest):
    def setUp(self):
        super(TestUsers, self).setUp()
        self.init_database()
        self.init_databaseData()
        self.req = self.dummy_request()

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
        self.DB.delete_user(1)
        usersFromDB = self.dbsession.query(User).all()
        experimentgroupsFromDB = self.dbsession.query(ExperimentGroup).all()
        dataitemsFromDB = self.dbsession.query(DataItem).all()

        user2 = self.dbsession.query(User).filter_by(id=2).one()
        dt3 = self.dbsession.query(DataItem).filter_by(id=3).one()
        dt4 = self.dbsession.query(DataItem).filter_by(id=4).one()

        assert usersFromDB == [user2]
        assert experimentgroupsFromDB[0].users == []
        assert dataitemsFromDB == [dt3, dt4]

    def getUser(self):
        usernames = self.dbsession.query(User.username).all()
        assert 'Example user' not in usernames
        exampleUser = self.DB.get_user('Example user')
        assert exampleUser.id == 3 and exampleUser.username == 'Example user'
        user1 = self.DB.get_user('First user')
        user2 = self.DB.get_user('Second user')
        assert user1.id == 1 and user1.username == 'First user'
        assert user2.id == 2 and user2.username == 'Second user'

    def test_assignUserToExperiment(self):
        user = self.dbsession.query(User).filter_by(id=1).one()
        self.DB.create_experimentgroup({'name': 'Example group'})
        expgroup = self.dbsession.query(ExperimentGroup).filter_by(id=3).one()
        self.DB.create_experiment(
            {'name': 'Example experiment',
             'startDatetime': '2016-01-01 00:00:00',
             'endDatetime': '2017-01-01 00:00:00',
             'size': 100,
             'experimentgroups': [expgroup]
             })
        experiment = self.dbsession.query(Experiment).filter_by(id=2).one()
        self.DB.assign_user_to_experiment(user.id, experiment.id)

        assert expgroup.users == [user]
        assert expgroup in user.experimentgroups

    def test_assignUserToExperiments(self):
        self.DB.create_user({'username': 'Test user'})
        user = self.dbsession.query(User).filter_by(username='Test user').one()
        assert user.experimentgroups == []
        self.DB.assign_user_to_experiments(3)
        expgroup1 = self.dbsession.query(ExperimentGroup).filter_by(id=1).one()
        expgroup2 = self.dbsession.query(ExperimentGroup).filter_by(id=2).one()
        assert expgroup1 in user.experimentgroups or expgroup2 in user.experimentgroups

    def test_getUsersForExperiment(self):
        usersForExperiment = self.DB.get_users_for_experiment(1)
        user1 = self.dbsession.query(User).filter_by(id=1).one()
        user2 = self.dbsession.query(User).filter_by(id=2).one()

        assert usersForExperiment == [user1, user2]

    def test_deleteUserFromExperiment(self):
        user = self.dbsession.query(User).filter_by(id=1).one()
        experimentgroup = user.experimentgroups[0]
        experiment = experimentgroup.experiment

        assert user in experimentgroup.users and experimentgroup in user.experimentgroups
        self.DB.delete_user_from_experiment(user.id, experiment.id)
        assert user not in experimentgroup.users and experimentgroup not in user.experimentgroups

    def test_getUsersForExperimentgroup(self):
        users = self.DB.get_users_for_experimentgroup(1)
        user1 = self.dbsession.query(User).filter_by(id=1).one()

        assert users == [user1]

# ---------------------------------------------------------------------------------
#                                  REST-Inteface
# ---------------------------------------------------------------------------------

class TestUsersREST(BaseTest):
    def setUp(self):
        super(TestUsersREST, self).setUp()
        self.init_database()
        self.init_databaseData()
        self.req = self.dummy_request()

    def test_user_GET(self):
        self.req.swagger_data = {'id': 1}
        httpUsers = Users(self.req)
        response = httpUsers.user_GET()
        user = {'id': 1, 'username': 'First user'}
        assert response == user

    def test_create_user(self):
        #TODO: Write test
        assert 1 == 1

    def test_configurations_GET(self):
        self.req.swagger_data = {'id': 1}
        httpUsers = Users(self.req)
        response = httpUsers.configurations_GET()
        configurations = [{'id': 1, 'experimentgroup_id': 1, 'value': 0.5, 'key': 'v1'},
                          {'id': 2, 'experimentgroup_id': 1, 'value': True, 'key': 'v2'}]

        assert response == configurations
        self.req.swagger_data = {'id': 3}
        httpUsers = Users(self.req)
        response = httpUsers.configurations_GET()
        assert response.status_code == 400

    def test_users_GET(self):
        httpUsers = Users(self.req)
        response = httpUsers.users_GET()
        result = response
        users = [{"id": 1, "username": "First user"},
                 {"id": 2, "username": "Second user"}]
        assert result == users

    def test_experiments_for_user_GET(self):
        self.req.swagger_data = {'id': 1}
        httpUsers = Users(self.req)
        response = httpUsers.experiments_for_user_GET()
        experiments = [{
             'id': 1,
             'application_id': None,
             'name': 'Test experiment',
             'size': 100,
             'startDatetime': '2016-01-01 00:00:00',
             'endDatetime': '2017-01-01 00:00:00',
             'experimentgroups': [{'id': 1, 'experiment_id': 1, 'name': 'Group A'}]
             }]

        assert response == experiments

    def test_events_POST(self):
        json_body = {
            'key': 'key1',
            'value': 10,
            'startDatetime': '2016-06-06 06:06:06',
            'endDatetime': '2016-06-07 06:06:06',
        }
        headers = {'username': 'First user'}
        self.req.json_body = json_body
        self.req.headers = headers
        httpUsers = Users(self.req)
        response = httpUsers.events_POST()
        result = response.json['data']
        dataitem = {'id': 5,
                    'key': 'key1',
                    'startDatetime': '2016-06-06 06:06:06',
                    'endDatetime': '2016-06-07 06:06:06',
                    'value': 10,
                    'user_id': 1}

        assert response.status_code == 200
        assert result == dataitem
        headers = {'username': 'fsdfdsf'}
        self.req.headers = headers
        httpUsers = Users(self.req)
        response = httpUsers.events_POST()
        assert response.status_code == 400

    def test_user_DELETE(self):
        self.req.swagger_data = {'id': 1}
        httpUsers = Users(self.req)
        response = httpUsers.user_DELETE()

        assert response == {}
        self.req.swagger_data = {'id': 3}
        httpUsers = Users(self.req)
        response = httpUsers.user_DELETE()
        assert response.status_code == 400
