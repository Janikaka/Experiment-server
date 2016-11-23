import datetime
from .base_test import BaseTest
from ..models import (Experiment, Client, DataItem, ExperimentGroup)
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

    def test_assignclientToExperiment(self):
        client = self.dbsession.query(Client).filter_by(id=1).one()
        self.DB.create_experimentgroup({'name': 'Example group'})
        expgroup = self.dbsession.query(ExperimentGroup).filter_by(id=3).one()
        self.DB.create_experiment(
            {'name': 'Example experiment',
             'startDatetime': '2016-01-01 00:00:00',
             'endDatetime': '2017-01-01 00:00:00',
             'experimentgroups': [expgroup]
             })
        experiment = self.dbsession.query(Experiment).filter_by(id=2).one()
        self.DB.assign_client_to_experiment(client.id, experiment.id)

        assert expgroup.clients == [client]
        assert expgroup in client.experimentgroups

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

    def test_client_has_applicationid_column(self):
        client = Client.get(1)
        is_error = False
        try:
            app_id = client.application_id
        except Exception as e:
            is_error = True
            pass

        assert not is_error

    def test_client_applicationid_can_be_set(self):
        client = Client.get(1)

        client.application_id = 1
        Client.save(client)

        assert Client.get(1).application_id is 1


# ---------------------------------------------------------------------------------
#                                  REST-Inteface
# ---------------------------------------------------------------------------------

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
        client = Client.get(1).as_dict()
        assert response == client

    def test_create_client(self):
        self.req.swagger_data = {'client': Client(clientname='Test client')}
        httpclients = Clients(self.req)
        response = httpclients.create_client()
        client = Client.get(3).as_dict()
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
        from sqlalchemy import asc
        self.req.swagger_data = {'appid': 1}
        httpclients = Clients(self.req)
        response = httpclients.clients_GET()
        result = response
        clients = list(map(lambda _: _.as_dict(), \
                    Client.query().filter(Client.application_id == 1)\
                        .order_by(asc(Client.id)).all()))
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
            'startDatetime': datetime.datetime(2016, 6, 6, 6, 6, 6),
            'endDatetime': datetime.datetime(2016, 6, 7, 6, 6, 6),
        }
        headers = {'clientname': 'First client'}
        self.req.json_body = json_body
        self.req.headers = headers
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
        headers = {'clientname': 'fsdfdsf'}
        self.req.headers = headers
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
