from pyramid.response import Response
from pyramid.view import view_config, view_defaults

import datetime
import random
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
def is_client_in_running_experiments(client):
    experiments = Experiment.query()\
        .join(ExperimentGroup)\
        .join(ExperimentGroup.clients).filter(Client.id == client.id).all()

    running_experiments = list(filter(lambda _: _.get_status() == 'running', experiments))

    return len(running_experiments) > 0

def assign_to_experiment(client, application):
    experiments = Experiment.query().join(Application)\
        .filter(Application.id == application.id)

    running_experiments = list(filter(lambda _: _.get_status() == 'running', experiments))
    try:
        return random.choice(running_experiments)
    except IndexError as e:
        print_log(datetime.datetime.now(), 'POST', '/configurations',
            'Get client configurations',
            'Failed: No running experiments on Application with id %s' % application.id)
        return None

def assign_to_experimentgroup(client, application):
    experiment = assign_to_experiment(client, application)

    try:
        expgroup = random.choice(list(experiment.experimentgroups))
    except AttributeError as e:
        # In this case, experiment is None, and has already been logged
        return None
    except IndexError as e:
        print_log(datetime.datetime.now(), 'POST', '/configurations',
            'Get client configurations',
            'Failed: No ExperimentGoups on Experiment with id %s' % experiment.id)
        return None

    if expgroup not in client.experimentgroups:
        client.experimentgroups.append(expgroup)
        Client.flush()

    return expgroup

def get_client_configurations(client, application):
    expgroup = assign_to_experimentgroup(client, application)

    try:
        configs =  list(map(lambda _: _.as_dict(), expgroup.configurations))
    except AttributeError as e:
        # In this case, experimentgroup is None, and has already been logged
        return None
    if len(configs) == 0:
        print_log(datetime.datetime.now(), 'POST', '/configurations',
            'Get client configurations',
            'Failed: No Configurations on ExperimentGroup with id %s' % expgroup.id)
        return None

    return configs

def get_client(name):
    client = Client.query().filter(Client.clientname == name).one_or_none()

    if client is None and len(name) > 0:
        client = Client(clientname=name)
        Client.save(client)

    return client

def get_client_by_id_and_app(data):
    try:
        app_id = data['appid']
        client_id = data['clientid']
    except KeyError as e:
        return None

    return Client.query()\
    .join(Client.experimentgroups)\
    .join(Experiment)\
    .join(Application)\
    .filter(Application.id == app_id)\
    .filter(Client.id == client_id)\
    .one_or_none()

def application_by_apikey_from_header(headers):
    apikey = None
    try:
        apikey = headers['authorization']
    except KeyError as e:
        return None

    app = Application.get_by('apikey', apikey)
    return app

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

    @view_config(route_name='configurations', request_method="OPTIONS")
    def all_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origins', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST')
        return res

    @view_config(route_name='events', request_method="OPTIONS")
    def all_Options(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origins', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST')
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
        result = get_client_by_id_and_app(self.request.swagger_data)

        if not result:
            print_log(datetime.datetime.now(), 'GET','applications/%s/clients/%s' \
                % (self.request.swagger_data['appid'], self.request.swagger_data['clientid']),
                'Get client', 'Failed')
            return self.createResponse(None, 400)
        return result.as_dict()

    # Delete client
    @view_config(route_name='client', request_method="DELETE")
    def client_DELETE(self):
        result = get_client_by_id_and_app(self.request.swagger_data)
        if not result:
            print_log(datetime.datetime.now(), 'DELETE', '/clients/' + str(id), 'Delete client', 'Failed')
            return self.createResponse(None, 400)
        Client.destroy(result)
        print_log(datetime.datetime.now(), 'DELETE', '/clients/' + str(id), 'Delete client', 'Succeeded')
        return {}

    # List configurations for specific client
    @view_config(route_name='configurations_for_client', request_method="GET")
    def configurations_GET(self):
        client = get_client_by_id_and_app(self.request.swagger_data)
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
        client = get_client_by_id_and_app(self.request.swagger_data)
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
        app = application_by_apikey_from_header(self.request.headers)
        if app is None:
            print_log(datetime.datetime.now(), 'POST', '/events', 'Save experiment data',
                'Unauthorized')
            return self.createResponse(None, 401)

        json = self.request.json_body
        value = json['value']
        key = json['key']
        startDatetime = datetime.datetime.strptime(json['startDatetime'], "%Y-%m-%d %H:%M:%S")
        endDatetime = datetime.datetime.strptime(json['endDatetime'], "%Y-%m-%d %H:%M:%S")


        clientname = self.request.headers['clientname']
        client = Client.get_by('clientname', clientname)
        if client is None:
            print_log(datetime.datetime.now(), 'POST', '/events', 'Save experiment data',
                'Failed: no client with name %s' % clientname)
            return self.createResponse(None, 400)
        if not is_client_in_running_experiments(client):
            print_log(datetime.datetime.now(), 'POST', '/events', 'Save experiment data',
                'Failed: client %s not in running experiments' % clientname)
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

    @view_config(route_name='configurations', request_method="POST")
    def configurations_POST(self):
        def print_error(message):
            print_log(datetime.datetime.now(), 'POST', '/configurations',
                'Get client configurations',
                message)

        app = application_by_apikey_from_header(self.request.headers)
        if app is None:
            print_error('Unauthorized')
            return self.createResponse(None, 401)

        try:
            req_clientname = self.request.swagger_data['clientname']
        except KeyError as e:
            print_error('Missing parameters')
            return self.createResponse(None, 400)

        client = get_client(req_clientname)
        configs = get_client_configurations(client, app)
        if configs is None:
            return self.createResponse(None, 400)

        return configs
