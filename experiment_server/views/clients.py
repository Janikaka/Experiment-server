from pyramid.response import Response
from pyramid.view import view_config, view_defaults

import datetime
from experiment_server.utils.log import print_log
from .webutils import WebUtils
from experiment_server.models.clients import Client
from experiment_server.models.dataitems import DataItem
from experiment_server.models.applications import Application
from experiment_server.models.experiments import Experiment
from experiment_server.models.experimentgroups import ExperimentGroup

from fn import _
from toolz import *

# Helper functions
def get_client_by_id_and_app(data):
    try:
        app_id = data['appid']
        client_id = data['clientid']

        return Client.query()\
        .join(Client.experimentgroups)\
        .join(Experiment)\
        .join(Application)\
        .filter(Application.id == app_id)\
        .filter(Client.id == client_id)\
        .one()
    except Exception as e:
        print_log(e)
        return None


@view_defaults(renderer='json')
class Clients(WebUtils):
    def __init__(self, request):
        self.request = request


    """
        CORS-options
    """
    @view_config(route_name='clients', request_method="OPTIONS")
    def all_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS, DELETE, PUT')
        return res

    @view_config(route_name='client', request_method="OPTIONS")
    def all_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS, DELETE, PUT')
        return res

    # List application's clients
    @view_config(route_name='clients', request_method="GET", renderer='json')
    def clients_GET(self):
        """
            Explanation: maps as_dict() -function to every client-object (this is returned by client.all())
            Creates a list and returns it. In future we might would like general json-serialization to make this even
            more simpler.
        """
        app_id = self.request.swagger_data['appid']

        if not Application.get(app_id):
            print_log('/applications/%s/clients failed' %app_id)
            return self.createResponse(None,400)

        clients = Client.query()\
        .join(Client.experimentgroups)\
        .join(Experiment)\
        .join(Application)\
        .filter(Application.id == app_id)

        return list(map(lambda _: _.as_dict(), clients))

    # Create new client
    @view_config(route_name='clients', request_method="POST", renderer='json')
    def create_client(self):
        req_client = self.request.swagger_data['client']
        client = Client(
            clientname=req_client.clientname
        )
        Client.save(client)
        return client.as_dict()

    # Get one client
    @view_config(route_name='client', request_method="GET", renderer='json')
    def client_GET(self):
        result = get_client_by_id_and_app(self.request.matchdict)

        if not result:
            print_log(datetime.datetime.now(), 'GET','applications/%s/clients/%s' % (client_id, app_id),
                'Get client', 'Failed')
            return self.createResponse(None, 400)
        return result.as_dict()

    # Delete client
    @view_config(route_name='client', request_method="DELETE")
    def client_DELETE(self):
        result = get_client_by_id_and_app(self.request.matchdict)
        if not result:
            print_log(datetime.datetime.now(), 'DELETE', '/clients/' + str(id), 'Delete client', 'Failed')
            return self.createResponse(None, 400)
        Client.destroy(result)
        print_log(datetime.datetime.now(), 'DELETE', '/clients/' + str(id), 'Delete client', 'Succeeded')
        return {}

    # List configurations for specific client
    @view_config(route_name='configurations_for_client', request_method="GET")
    def configurations_GET(self):
        client = get_client_by_id_and_app(self.request.matchdict)
        client_id = self.request.swagger_data['clientid']
        app_id = self.request.swagger_data['appid']
        if client is None:
            print_log(datetime.datetime.now(), 'GET', '/applications/%s/clients/%s/configurations failed' % (app_id, client_id),
                'List configurations for specific client', 'Failed')
            return self.createResponse(None, 400)

        current_groups = client.experimentgroups
        configs = list(map(lambda _: _.configurations, current_groups))
        result = list(map(lambda _: _.as_dict(), list(concat(configs))))
        return result

    # List all experiments for specific client
    @view_config(route_name='experiments_for_client', request_method="GET")
    def experiments_for_client_GET(self):
        client = get_client_by_id_and_app(self.request.matchdict)
        app_id = self.request.swagger_data['appid']
        if not client:
            return self.createResponse(None, 400)

        experiments = Experiment.query()\
        .filter(Experiment.application_id == app_id)\
        .join(ExperimentGroup)\
        .join(ExperimentGroup.clients)\
        .filter(Client.id == client.id)

        print(experiments)
        result = map(lambda _: _.as_dict(), experiments)
        return list(result)

    # Save experiment data
    @view_config(route_name='events', request_method="POST")
    def events_POST(self):
        json = self.request.json_body
        value = json['value']
        key = json['key']
        startDatetime = json['startDatetime']
        endDatetime = json['endDatetime']
        clientname = self.request.headers['clientname']
        client = Client.get_by('clientname', clientname)
        if client is None:
            print_log(datetime.datetime.now(), 'POST', '/events', 'Save experiment data',
                'Failed')
            return self.createResponse(None, 400)
        result = DataItem(
            client=client,
            value=value,
            key=key,
            startDatetime=startDatetime,
            endDatetime=endDatetime
        )
        DataItem.save(result)
        print_log(datetime.datetime.now(), 'POST', '/events', 'Save experiment data', result)
        return result.as_dict()
