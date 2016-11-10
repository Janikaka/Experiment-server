from pyramid.response import Response
from pyramid.view import view_config, view_defaults

import datetime
from experiment_server.utils.log import print_log
from .webutils import WebUtils
from experiment_server.models.clients import client
from experiment_server.models.dataitems import DataItem

from fn import _
from toolz import *

@view_defaults(renderer='json')
class clients(WebUtils):
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

    # List all clients
    @view_config(route_name='clients', request_method="GET", renderer='json')
    def clients_GET(self):
        """
            Explanation: maps as_dict() -function to every client-object (this is returned by client.all())
            Creates a list and returns it. In future we might would like general json-serialization to make this even
            more simpler.
        """
        return list(map(lambda _: _.as_dict(), client.all()))

    # Create new client
    @view_config(route_name='clients', request_method="POST", renderer='json')
    def create_client(self):
        req_client = self.request.swagger_data['client']
        client = client(
            clientname=req_client.clientname
        )
        client.save(client)
        return client.as_dict()

    # Get one client
    @view_config(route_name='client', request_method="GET", renderer='json')
    def client_GET(self):
        id = self.request.swagger_data['id']
        result = client.get(id)
        if not result:
            print_log('/clients/%s failed' % id)
            return self.createResponse(None, 400)
        return result.as_dict()

    # Delete client
    @view_config(route_name='client', request_method="DELETE")
    def client_DELETE(self):
        id = self.request.swagger_data['id']
        result = client.get(id)
        if not result:
            print_log(datetime.datetime.now(), 'DELETE', '/clients/' + str(id), 'Delete client', 'Failed')
            return self.createResponse(None, 400)
        client.destroy(result)
        print_log(datetime.datetime.now(), 'DELETE', '/clients/' + str(id), 'Delete client', 'Succeeded')
        return {}

    # List configurations for specific client
    @view_config(route_name='configurations', request_method="GET")
    def configurations_GET(self):
        id = self.request.swagger_data['id']
        client = client.get(id)
        if client is None:
            print_log(datetime.datetime.now(), 'GET', '/configurations', 'List configurations for specific client', None)
            return self.createResponse(None, 400)

        current_groups = client.experimentgroups
        configs = list(map(lambda _: _.configurations, current_groups))
        result = list(map(lambda _: _.as_dict(), list(concat(configs))))
        return result

    # List all experiments for specific client
    @view_config(route_name='experiments_for_client', request_method="GET")
    def experiments_for_client_GET(self):
        id = self.request.swagger_data['id']
        client = client.get(id)
        if not client:
            return self.createResponse(None, 400)
        clients_experimentgroups = client.experimentgroups
        experiments = map(lambda _: _.experiment, clients_experimentgroups)
        # TODO: Add experimentgroups (= client's experimentgroups of that experiment) to experiment
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
        client = client.get_by('clientname', clientname)
        if client is None:
            print_log(datetime.datetime.now(), 'POST', '/events', 'Save experiment data', None)
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
