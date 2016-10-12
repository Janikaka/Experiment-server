import datetime
from .base_test import BaseTest
from ..models import (Experiment, User, ExperimentGroup, Configuration)
from experiment_server.views.experiments import Experiments


def strToDatetime(date):
    return datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------------------------
#                                DatabaseInterface
# ---------------------------------------------------------------------------------


class TestExperiments(BaseTest):
    def setUp(self):
        super(TestExperiments, self).setUp()
        self.init_database()
        self.init_databaseData()
        self.req = self.dummy_request()

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
        self.DB.delete_experiment(1)
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
        status = self.DB.get_status_for_experiment(1)
        assert status == 'running'
        newEndDatetime = strToDatetime('2016-06-01 00:00:00')
        self.dbsession.query(Experiment).filter_by(id=1).one().endDatetime = newEndDatetime
        status = self.DB.get_status_for_experiment(1)
        assert status == 'finished'
        newStartDatetime = strToDatetime('2017-01-01 00:00:00')
        newEndDatetime = strToDatetime('2017-06-01 00:00:00')
        self.dbsession.query(Experiment).filter_by(id=1).one().startDatetime = newStartDatetime
        self.dbsession.query(Experiment).filter_by(id=1).one().endDatetime = newEndDatetime
        status = self.DB.get_status_for_experiment(1)
        assert status == 'waiting'

    def test_getAllRunningExperiments(self):
        experiments = self.DB.get_all_running_experiments()
        experimentsFromDB = self.dbsession.query(Experiment).all()

        assert experiments == experimentsFromDB

    def test_getExperimentsUserParticipates(self):
        expForUser1 = self.DB.get_user_experiments_list(1)
        expForUser2 = self.DB.get_user_experiments_list(2)
        experimentsFromDB = self.dbsession.query(Experiment).all()

        assert expForUser1 == [experimentsFromDB[0]]
        assert expForUser2 == [experimentsFromDB[0]]


# ---------------------------------------------------------------------------------
#                                  REST-Inteface
# ---------------------------------------------------------------------------------


class TestExperimentsREST(BaseTest):
    def setUp(self):
        super(TestExperimentsREST, self).setUp()
        self.init_database()
        self.init_databaseData()
        self.req = self.dummy_request()

    def test_experiments_POST(self):
        json_body = {'name': 'Example Experiment',
                     'application_id': None,
                     'startDatetime': '2016-01-01 00:00:00',
                     'endDatetime': '2017-01-01 00:00:00',
                     'size': 100,
                     'experimentgroups': [
                         {'name': 'expgroup',
                          'configurations': [{'key': 'key1', 'value': 10}]
                          }]
                     }
        self.req.json_body = json_body
        httpExperiments = Experiments(self.req)
        response = httpExperiments.experiments_POST()
        result = response.json['data']
        experiment = {'id': 2,
                      'application_id': None,
                      'name': 'Example Experiment',
                      'size': 100,
                      'startDatetime': '2016-01-01 00:00:00',
                      'endDatetime': '2017-01-01 00:00:00'}

        assert response.status_code == 200
        assert result == experiment

    def test_experiments_GET(self):
        httpExperiments = Experiments(self.req)
        response = httpExperiments.experiments_GET()
        result = response.json['data']
        experiment = result[0]

        assert len(result) == 1
        assert response.status_code == 200
        assert experiment['id'] == 1
        assert experiment['name'] == 'Test experiment'
        assert experiment['startDatetime'] == '2016-01-01 00:00:00'
        assert experiment['endDatetime'] == '2017-01-01 00:00:00'
        assert experiment['size'] == 100
        assert experiment['status'] == 'running'

    def test_experiment_metadata_GET(self):
        self.req.matchdict = {'id': 1}
        httpExperiments = Experiments(self.req)
        response = httpExperiments.experiment_metadata_GET()
        result = response.json['data']
        experiment = {'id': 1,
                      'name': 'Test experiment',
                      'application_id': None,
                      'startDatetime': '2016-01-01 00:00:00',
                      'endDatetime': '2017-01-01 00:00:00',
                      'status': 'running',
                      'size': 100,
                      'totalDataitems': 4,
                      'experimentgroups':
                          [{'id': 1,
                            'name': 'Group A',
                            'users': [{'id': 1, 'username': 'First user'}],
                            'experiment_id': 1,
                            'configurations':
                                [{'id': 1, 'key': 'v1', 'value': 0.5, 'experimentgroup_id': 1},
                                 {'id': 2, 'key': 'v2', 'value': True, 'experimentgroup_id': 1}]
                            },
                           {'id': 2,
                            'name': 'Group B',
                            'users': [{'id': 2, 'username': 'Second user'}],
                            'experiment_id': 1,
                            'configurations':
                                [{'id': 3, 'key': 'v1', 'value': 1.0, 'experimentgroup_id': 2},
                                 {'id': 4, 'key': 'v2', 'value': False, 'experimentgroup_id': 2}]
                            }]
                      }

        assert result == experiment
        assert response.status_code == 200

        self.req.matchdict = {'id': 2}
        httpExperiments = Experiments(self.req)
        response = httpExperiments.experiment_metadata_GET()
        assert response.status_code == 400
        assert response.json == None

    def test_experiment_DELETE(self):
        self.req.matchdict = {'id': 1}
        httpExperiments = Experiments(self.req)
        response = httpExperiments.experiment_DELETE()

        assert response.status_code == 200
        self.req.matchdict = {'id': 2}
        print(self.req.matchdict)
        httpExperiments = Experiments(self.req)
        response = httpExperiments.experiment_DELETE()
        assert response.status_code == 400
        assert response.json == None

    def test_users_for_experiment_GET(self):
        self.req.swagger_data = {'id': 1}
        httpExperiments = Experiments(self.req)
        response = httpExperiments.users_for_experiment_GET()
        result = response.json['data']
        users = [{'id': 1,
                  'username': 'First user',
                  'experimentgroup': {'name': 'Group A', 'id': 1, 'experiment_id': 1},
                  'totalDataitems': 2},
                 {'id': 2,
                  'username': 'Second user',
                  'experimentgroup': {'name': 'Group B', 'id': 2, 'experiment_id': 1},
                  'totalDataitems': 2}]

        assert response.status_code == 200
        assert result == users
        self.req.matchdict = {'id': 2}
        httpExperiments = Experiments(self.req)
        response = httpExperiments.users_for_experiment_GET()
        assert response.status_code == 400
        assert response.json == None

    def test_experiment_data_GET(self):
        # TODO
        assert 1 == 1

    def test_experimentgroup_GET(self):
        self.req.matchdict = {'expgroupid': 1, 'expid': 1}
        httpExperiments = Experiments(self.req)
        response = httpExperiments.experimentgroup_GET()
        result = response.json['data']
        experimentgroup = {'id': 1,
                           'configurations': [
                               {'experimentgroup_id': 1, 'key': 'v1', 'id': 1, 'value': 0.5},
                               {'experimentgroup_id': 1, 'key': 'v2', 'id': 2, 'value': True}],
                           'totalDataitems': 2,
                           'name': 'Group A',
                           'experiment_id': 1,
                           'users': [{'id': 1, 'username': 'First user'}]}

        assert response.status_code == 200
        assert result == experimentgroup
        self.req.matchdict = {'expgroupid': 1, 'expid': 2}
        httpExperiments = Experiments(self.req)
        response = httpExperiments.experimentgroup_GET()
        assert response.status_code == 400
        assert response.json == None

    def test_experimentgroup_DELETE(self):
        self.req.matchdict = {'expgroupid': 1, 'expid': 1}
        httpExperiments = Experiments(self.req)
        response = httpExperiments.experimentgroup_DELETE()

        assert response.status_code == 200
        self.req.matchdict = {'expgroupid': 2, 'expid': 2}
        httpExperiments = Experiments(self.req)
        response = httpExperiments.experimentgroup_DELETE()
        assert response.status_code == 400

    def test_user_for_experiment_DELETE(self):
        self.req.matchdict = {'userid': 1, 'expid': 1}
        httpExperiments = Experiments(self.req)
        response = httpExperiments.user_for_experiment_DELETE()

        assert response.status_code == 200
        self.req.matchdict = {'userid': 2, 'expid': 2}
        httpExperiments = Experiments(self.req)
        response = httpExperiments.user_for_experiment_DELETE()
        assert response.status_code == 400
