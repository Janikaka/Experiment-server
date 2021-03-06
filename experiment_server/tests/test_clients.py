import datetime
from .base_test import BaseTest
from ..models import (Application, Configuration, Experiment, Client, DataItem, ExperimentGroup)
from experiment_server.views.clients import Clients


# ---------------------------------------------------------------------------------
#                                DatabaseInterface
# ---------------------------------------------------------------------------------

class TestClients(BaseTest):
    def setUp(self):
        super(TestClients, self).setUp()
        self.init_database()
        self.init_databaseData()

    def test_createclient(self):
        clientsFromDB = self.dbsession.query(Client).all()
        experimentgroupsFromDB = self.dbsession.query(ExperimentGroup).all()
        dataitemsFromDB = self.dbsession.query(DataItem).all()
        client1 = {
            'id': 1,
            'clientname': 'First client',
            'experimentgroups': [experimentgroupsFromDB[0]],
            'dataitems': [dataitemsFromDB[0], dataitemsFromDB[1]]
        }
        client2 = {
            'id': 2,
            'clientname': 'Second client',
            'experimentgroups': [experimentgroupsFromDB[1]],
            'dataitems': [dataitemsFromDB[2], dataitemsFromDB[3]]
        }
        clients = [client1, client2]

        for i in range(len(clientsFromDB)):
            for key in clients[i]:
                assert getattr(clientsFromDB[i], key) == clients[i][key]

    def test_deleteclient(self):
        self.DB.delete_client(1)
        clientsFromDB = self.dbsession.query(Client).all()
        experimentgroupsFromDB = self.dbsession.query(ExperimentGroup).all()
        dataitemsFromDB = self.dbsession.query(DataItem).all()

        client2 = self.dbsession.query(Client).filter_by(id=2).one()
        dt3 = self.dbsession.query(DataItem).filter_by(id=3).one()
        dt4 = self.dbsession.query(DataItem).filter_by(id=4).one()

        assert clientsFromDB == [client2]
        assert experimentgroupsFromDB[0].clients == []
        assert dataitemsFromDB == [dt3, dt4]

    def getclient(self):
        clientnames = self.dbsession.query(client.clientname).all()
        assert 'Example client' not in clientnames
        exampleclient = self.DB.get_client('Example client')
        assert exampleclient.id == 3 and exampleclient.clientname == 'Example client'
        client1 = self.DB.get_client('First client')
        client2 = self.DB.get_client('Second client')
        assert client1.id == 1 and client1.clientname == 'First client'
        assert client2.id == 2 and client2.clientname == 'Second client'

    def test_assignclientToExperiments(self):
        self.DB.create_client({'clientname': 'Test client'})
        client = self.dbsession.query(Client).filter_by(clientname='Test client').one()
        assert client.experimentgroups == []
        self.DB.assign_client_to_experiments(3)
        expgroup1 = self.dbsession.query(ExperimentGroup).filter_by(id=1).one()
        expgroup2 = self.dbsession.query(ExperimentGroup).filter_by(id=2).one()
        assert expgroup1 in client.experimentgroups or expgroup2 in client.experimentgroups

    def test_getclientsForExperiment(self):
        clientsForExperiment = self.DB.get_clients_for_experiment(1)
        client1 = self.dbsession.query(Client).filter_by(id=1).one()
        client2 = self.dbsession.query(Client).filter_by(id=2).one()

        assert clientsForExperiment == [client1, client2]

    def test_deleteclientFromExperiment(self):
        client = self.dbsession.query(Client).filter_by(id=1).one()
        experimentgroup = client.experimentgroups[0]
        experiment = experimentgroup.experiment

        assert client in experimentgroup.clients and experimentgroup in client.experimentgroups
        self.DB.delete_client_from_experiment(client.id, experiment.id)
        assert client not in experimentgroup.clients and experimentgroup not in client.experimentgroups

    def test_getclientsForExperimentgroup(self):
        clients = self.DB.get_clients_for_experimentgroup(1)
        client1 = self.dbsession.query(Client).filter_by(id=1).one()

        assert clients == [client1]

# ---------------------------------------------------------------------------------
#                                  REST-Inteface
# ---------------------------------------------------------------------------------

def get_datetime(year, month, day, hour, minute, second):
    now = datetime.datetime.now()
    return datetime.datetime(
            sum([now.year, year]),
            sum([now.month, month]),
            sum([now.day, day]),
            sum([now.hour, hour]),
            sum([now.minute, minute]),
            sum([now.second, second]))

class TestClientsREST(BaseTest):
    def setUp(self):
        super(TestClientsREST, self).setUp()
        self.init_database()
        self.init_databaseData()
        self.req = self.dummy_request()

    def test_client_GET(self):
        self.req.swagger_data = {'appid': 1, 'clientid' : 1}
        httpclients = Clients(self.req)
        response = httpclients.client_GET()
        client = {'id': 1, 'clientname': 'First client'}
        assert response == client

    def test_create_client(self):
        self.req.swagger_data = {'client': Client(clientname='Test client')}
        httpclients = Clients(self.req)
        response = httpclients.create_client()
        client = {'id': 3, 'clientname': 'Test client'}
        assert response == client

    def test_configurations_GET(self):
        self.req.swagger_data = {'appid': 1, 'clientid': 1}
        httpclients = Clients(self.req)
        response = httpclients.configurations_GET()
        configurations = [{'id': 1, 'experimentgroup_id': 1, 'value': 0.5, 'key': 'v1'},
                          {'id': 2, 'experimentgroup_id': 1, 'value': True, 'key': 'v2'}]

        assert response == configurations
        self.req.swagger_data = {'appid':1, 'clientid': 3}
        httpclients = Clients(self.req)
        response = httpclients.configurations_GET()
        assert response.status_code == 400

    def test_clients_GET(self):
        self.req.swagger_data = {'appid': 1}
        httpclients = Clients(self.req)
        response = httpclients.clients_GET()
        result = response
        clients = [{"id": 1, "clientname": "First client"},
                 {"id": 2, "clientname": "Second client"}]
        assert result == clients

    def test_experiments_for_client_GET(self):
        self.req.swagger_data = {'appid': 1, 'clientid': 1}
        httpclients = Clients(self.req)
        response = httpclients.experiments_for_client_GET()
        experiments = [{
             'id': 1,
             'application_id': 1,
             'name': 'Test experiment',
             'startDatetime': '2016-01-01 00:00:00',
             'endDatetime': '2017-01-01 00:00:00'
             # TODO: Add experimentgroups to experiment (views/experiments experiments_for_client_GET())
             #'experimentgroups': [{'id': 1, 'experiment_id': 1, 'name': 'Group A'}]
             }]

        assert response == experiments

    def test_events_POST(self):
        json_body = {
            'key': 'key1',
            'value': 10,
            'startDatetime': str(datetime.datetime(2016, 6, 6, 6, 6, 6)),
            'endDatetime': str(datetime.datetime(2016, 6, 7, 6, 6, 6)),
        }

        headers = {'clientname': 'First client'}
        self.req.json_body = json_body
        self.req.headers = headers
        self.req.headers['authorization'] = Application.get(1).apikey

        httpclients = Clients(self.req)
        response = httpclients.events_POST()
        #result = response.json['data']
        dataitem = {'id': 5,
                    'key': 'key1',
                    'startDatetime': '2016-06-06 06:06:06',
                    'endDatetime': '2016-06-07 06:06:06',
                    'value': 10,
                    'client_id': 1}

        assert response == dataitem

    def test_events_POST_nonexistent_client(self):
        self.req.headers = {'clientname': 'fsdfdsf'}
        self.req.headers['authorization'] = Application.get(1).apikey
        self.req.json_body = {
            'key': 'key1',
            'value': 10,
            'startDatetime': str(datetime.datetime(2016, 6, 6, 6, 6, 6)),
            'endDatetime': str(datetime.datetime(2016, 6, 7, 6, 6, 6)),
        }
        httpclients = Clients(self.req)
        response = httpclients.events_POST()
        assert response.status_code == 400

    def test_events_POST_no_apikey(self):
        self.req.headers['clientname'] = 'First client'
        self.req.json_body = {
            'key': 'key1',
            'value': 10,
            'startDatetime': str(datetime.datetime(2016, 6, 6, 6, 6, 6)),
            'endDatetime': str(datetime.datetime(2016, 6, 7, 6, 6, 6)),
        }
        httpclients = Clients(self.req)
        response = httpclients.events_POST()
        assert response.status_code == 401

    def test_events_POST_client_not_in_running_experiment(self):
        client = Client(clientname='Wheatley')
        Client.save(client)
        client = Client.get_by('clientname', 'Wheatley')

        expgroup = ExperimentGroup(name='Cake', id=59, clients=[client])
        ExperimentGroup.save(expgroup)

        app = Application.get(1)

        start = get_datetime(-2, 0, 0, 0, 0, 0)
        end = get_datetime(-1, 0, 0, 0, 0, 0)
        experiment = Experiment(name='Non-running Test Experiment', application_id=5,
        startDatetime=start,
        endDatetime=end,
        experimentgroups=[ExperimentGroup.get(59)],
        application=app)
        Experiment.save(experiment)

        self.req.headers['clientname'] = 'Wheatley'
        self.req.headers['authorization'] = app.apikey
        self.req.json_body = {
            'key': 'key1',
            'value': 10,
            'startDatetime': str(datetime.datetime(2016, 6, 6, 6, 6, 6)),
            'endDatetime': str(datetime.datetime(2016, 6, 7, 6, 6, 6)),
        }
        httpclients = Clients(self.req)
        response = httpclients.events_POST()
        assert response.status_code == 400

    def test_client_DELETE(self):
        self.req.swagger_data = {'appid': 1, 'clientid': 1}
        httpclients = Clients(self.req)
        response = httpclients.client_DELETE()

        assert response == {}
        self.req.swagger_data = {'id': 3}
        httpclients = Clients(self.req)
        response = httpclients.client_DELETE()
        assert response.status_code == 400

    def test_configurations_POST_no_apikey(self):
        self.req.swagger_data = {'clientname': 'new Tester'}
        httpclients = Clients(self.req)
        response = httpclients.configurations_POST()

        assert response.status_code == 401

    def test_configurations_POST_no_name(self):
        self.req.headers['authorization'] = Application.get(1).apikey
        self.req.swagger_data = {}
        httpclients = Clients(self.req)
        response = httpclients.configurations_POST()

        assert response.status_code == 400

    def test_configurations_POST_creates_client_if_nonexistent(self):
        count_clients_before = Client.query().count()

        self.req.headers['authorization'] = Application.get(1).apikey
        self.req.swagger_data = {'clientname': 'another tester'}
        httpclients = Clients(self.req)
        response = httpclients.configurations_POST()

        assert Client.query().count() > count_clients_before

    def test_configurations_POST_assigns_user_to_experimentgroup(self):
        count_experimentgroup_clients_before = Client.query()\
            .join(Client.experimentgroups)\
            .filter(ExperimentGroup.id == 42)\
            .count()

        self.req.headers['authorization'] = Application.get(2).apikey
        self.req.swagger_data = {'clientname': 'Chell'}
        httpclients = Clients(self.req)
        response = httpclients.configurations_POST()

        count_experimentgroup_clients_after = Client.query()\
            .join(Client.experimentgroups)\
            .filter(ExperimentGroup.id == 42)\
            .count()

        assert count_experimentgroup_clients_after > count_experimentgroup_clients_before

    def test_configurations_POST_client_not_created_if_exists_in_application(self):
        httpclients = Clients(self.req)

        self.req.headers['authorization'] = Application.get(1).apikey
        self.req.swagger_data = {'clientname': 'Chell'}
        httpclients.configurations_POST()

        count_clients_before = Client.query().count()

        self.req.headers['authorization'] = Application.get(1).apikey
        self.req.swagger_data = {'clientname': 'Chell'}
        httpclients.configurations_POST()

        count_clients_after = Client.query().count()

        assert count_clients_after == count_clients_before

    def test_configurations_POST_no_running_experiments(self):
        import uuid

        app = Application(name='Science', id=5, apikey=str(uuid.uuid4()))
        Application.save(app)

        expgroup = ExperimentGroup(name='Cake', id=59)
        ExperimentGroup.save(expgroup)

        conf = Configuration(key='v9', value=False, experimentgroup_id=expgroup.id)
        Configuration.save(conf)

        start = get_datetime(-2, 0, 0, 0, 0, 0)
        end = get_datetime(-1, 0, 0, 0, 0, 0)
        experiment = Experiment(name='Non-running Test Experiment', application_id=5,
        startDatetime=start,
        endDatetime=end,
        experimentgroups=[ExperimentGroup.get(59)])
        Experiment.save(experiment)

        httpclients = Clients(self.req)
        self.req.headers['authorization'] = Application.get(5).apikey
        self.req.swagger_data = {'clientname': 'Chell'}
        response = httpclients.configurations_POST()

        assert response.status_code == 400

    def test_configurations_POST_no_experimentgroups(self):
        import uuid

        app = Application(name='Science', id=5, apikey=str(uuid.uuid4()))
        Application.save(app)

        start = get_datetime(-1, 0, 0, 0, 0, 0)
        end = get_datetime(1, 0, 0, 0, 0, 0)

        experiment = Experiment(name='Test Experiment without Experimentgroups', application_id=5,
        startDatetime=start,
        endDatetime=end,
        experimentgroups=[])
        Experiment.save(experiment)

        httpclients = Clients(self.req)
        self.req.headers['authorization'] = Application.get(5).apikey
        self.req.swagger_data = {'clientname': 'Chell'}
        response = httpclients.configurations_POST()

        assert response.status_code == 400

    def test_configurations_POST_no_configurations(self):
        import uuid

        app = Application(name='Science', id=5, apikey=str(uuid.uuid4()))
        Application.save(app)

        expgroup = ExperimentGroup(name='Cake', id=59)
        ExperimentGroup.save(expgroup)

        start = get_datetime(-2, 0, 0, 0, 0, 0)
        end = get_datetime(1, 0, 0, 0, 0, 0)
        experiment = Experiment(name='Test Experiment without Configurations', application_id=5,
        startDatetime=start,
        endDatetime=end,
        experimentgroups=[ExperimentGroup.get(59)])
        Experiment.save(experiment)

        httpclients = Clients(self.req)
        self.req.headers['authorization'] = Application.get(5).apikey
        self.req.swagger_data = {'clientname': 'Chell'}
        response = httpclients.configurations_POST()

        assert response.status_code == 400

    def test_configurations_POST_new_client(self):
        httpclients = Clients(self.req)
        self.req.headers['authorization'] = Application.get(1).apikey
        self.req.swagger_data = {'clientname': 'Chell'}
        response = httpclients.configurations_POST()

        expected1 = list(map(lambda _: _.as_dict(), \
            Configuration.query()\
                .join(ExperimentGroup)\
                .filter(ExperimentGroup.id == 1).all()))
        expected2 = list(map(lambda _: _.as_dict(), \
            Configuration.query()\
                .join(ExperimentGroup)\
                .filter(ExperimentGroup.id == 2).all()))

        assert response == expected1 or response == expected2

    def test_configurations_POST_existing_client(self):
        httpclients = Clients(self.req)
        self.req.headers['authorization'] = Application.get(1).apikey
        self.req.swagger_data = {'clientname': 'First client'}
        response = httpclients.configurations_POST()

        expected1 = list(map(lambda _: _.as_dict(), \
            Configuration.query()\
                .join(ExperimentGroup)\
                .filter(ExperimentGroup.id == 1).all()))
        expected2 = list(map(lambda _: _.as_dict(), \
            Configuration.query()\
                .join(ExperimentGroup)\
                .filter(ExperimentGroup.id == 2).all()))

        assert response == expected1 or response == expected2
