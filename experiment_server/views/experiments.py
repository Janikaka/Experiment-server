""" Imports """
import datetime
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from experiment_server.utils.log import print_log
from experiment_server.views.webutils import WebUtils

from experiment_server.models.clients import client
from experiment_server.models.experiments import Experiment
from experiment_server.models.experimentgroups import ExperimentGroup

from toolz import assoc, concat

@view_defaults(renderer='json')
class Experiments(WebUtils):
    def __init__(self, request):
        self.request = request

    """
        CORS-options
    """
    @view_config(route_name='experiments', request_method="OPTIONS")
    def all_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS, DELETE, PUT')
        return res

    @view_config(route_name='experiment', request_method="OPTIONS")
    def all_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS, DELETE, PUT')
        return res

    @view_config(route_name='experimentgroup', request_method="OPTIONS")
    def all_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS, DELETE, PUT')
        return res

    @view_config(route_name='experiments', request_method="POST")
    def experiments_POST(self):
        """ Create new experiment """
        req_exp = self.request.swagger_data['experiment']
        exp = Experiment(
                name=req_exp.name,
                startDatetime = req_exp.startDatetime,
                endDatetime = req_exp.endDatetime,
                size = req_exp.size,
                application_id = req_exp.application_id
        )
        Experiment.save(exp)
        print_log(req_exp.name, 'POST', '/experiments', 'Create new experiment', exp)
        return exp.as_dict()

    @view_config(route_name='experiments', request_method="GET")
    def experiments_GET(self):
        """ List all experiments """
        experiments = []
        for exp in Experiment.all():
            status = exp.get_status()
            exp_with_status = assoc(exp.as_dict(), 'status', status)
            experiments.append(exp_with_status)
        return experiments

    @view_config(route_name='experiment', request_method="GET", renderer='json')
    def experiments_GET_one(self):
        """ Find and return one experiment by id with GET method """
        exp_id = self.request.swagger_data['id']
        exp = Experiment.get(exp_id)
        if exp is None:
            print_log(datetime.datetime.now(), 'GET', '/experiments/' + str(exp_id), 'Get one experiment', None)
            return self.createResponse(None, 400)
        return exp.as_dict()

    @view_config(route_name='experiment', request_method="DELETE")
    def experiment_DELETE(self):
        """ Delete one experiment """
        exp_id = self.request.swagger_data['id']
        exp = Experiment.get(exp_id)
        if not exp:
            print_log(datetime.datetime.now(), 'DELETE', '/experiments/' + str(exp_id), 'Delete experiment', 'Failed')
            return self.createResponse(None, 400)
        Experiment.destroy(exp)
        print_log(datetime.datetime.now(), 'DELETE', '/experiments/' + str(exp_id), 'Delete experiment', 'Succeeded')
        return {}

    @view_config(route_name='experiment_metadata', request_method="GET")
    def experiment_metadata_GET(self):
        id = int(self.request.matchdict['id'])
        experiment = Experiment.get(id)
        if experiment is None:
            print_log(datetime.datetime.now(), 'GET', '/experiments/' + str(id) + '/metadata',
                     'Show specific experiment metadata', None)
            return self.createResponse(None, 400)
        experimentAsJSON = experiment.as_dict()
        totalDataitems = experiment.get_total_dataitems()
        experimentgroups = []
        for i in range(len(experiment.experimentgroups)):
            expgroup = experiment.experimentgroups[i]
            expgroupAsJSON = expgroup.as_dict()
            confs = expgroup.configurations
            clients = []
            for i in range(len(expgroup.clients)):
                clients.append(expgroup.clients[i].as_dict())
            configurations = []
            for i in range(len(confs)):
                configurations.append(confs[i].as_dict())
            expgroupAsJSON['configurations'] = configurations
            expgroupAsJSON['clients'] = clients
            experimentgroups.append(expgroupAsJSON)
        experimentAsJSON['experimentgroups'] = experimentgroups
        experimentAsJSON['totalDataitems'] = totalDataitems
        experimentAsJSON['status'] = experiment.get_status()
        result = {'data': experimentAsJSON}
        print_log(datetime.datetime.now(), 'GET', '/experiments/' + str(id) + '/metadata',
                 'Show specific experiment metadata', result)
        return self.createResponse(result, 200)

    @view_config(route_name='clients_for_experiment', request_method="GET")
    def clients_for_experiment_GET(self):
        """ List all clients for specific experiment """
        id = self.request.swagger_data['id']
        exp = Experiment.get(id)
        if exp is None:
            print_log(datetime.datetime.now(), 'GET', '/experiments/' + str(id) + '/clients',
                      'List all clients for specific experiment', None)
            return self.createResponse(None, 400)
        clients = []
        for expgroup in exp.experimentgroups:
            clients.extend(map(lambda _: _.as_dict(), expgroup.clients))
        return list(clients)

    @view_config(route_name='client_for_experiment', request_method="DELETE")
    def client_for_experiment_DELETE(self):
        """ Delete client from specific experiment """
        expid = self.request.swagger_data['expid']
        clientid = self.request.swagger_data['clientid']
        client = client.get(clientid)
        exp = Experiment.get(expid)
        if not exp or not clientid or not client:
            print_log(datetime.datetime.now(),
                      'GET', '/experiments/' + str(expid) + '/clients/' + str(clientid),
                      'Delete client from specific experiment', 'Failed')
            return self.createResponse(None, 400)

        clients_exp_groups = list(filter(lambda expgroup: expgroup.experiment_id == expid, client.experimentgroups))

        for eg in clients_exp_groups:
            client.experimentgroups.remove(eg)

        return {}

    @view_config(route_name='experiment_data', request_method="GET")
    def experiment_data_GET(self):
        """ Show one experiment data, including experiment and experimentgroups """
        expId = self.request.swagger_data['id']
        experiment = Experiment.get(expId)
        if experiment is None:
            print_log(datetime.datetime.now(), 'GET', '/experiments/' + str(id) + '/data',
                      'Get all things and experimentgroups of one experiment', None)
            return self.createResponse(None, 400)
        expgroups = list(map(lambda _: _.as_dict(), experiment.experimentgroups))
        experimentAsJSON = experiment.as_dict()
        result = assoc(experimentAsJSON, 'experimentgroups', expgroups)
        return result

    @view_config(route_name='experimentgroup', request_method="GET")
    def experimentgroup_GET(self):
        """ Show specific experiment group metadata """
        expgroupid = self.request.swagger_data['expgroupid']
        expid = self.request.swagger_data['expid']
        expgroup = ExperimentGroup.get(expgroupid)

        if expgroup is None or expgroup.experiment.id != expid:
            print_log(datetime.datetime.now(), 'GET',
                      '/experiments/' + str(expid) + '/experimentgroups/' + str(expgroupid),
                      'Show specific experimentgroup metadata', None)
            return self.createResponse(None, 400)

        configurations = list(map(lambda _: _.as_dict(), expgroup.configurations))
        clients = list(map(lambda _: _.as_dict(), expgroup.clients))
        dataitems = list(map(lambda _: _.dataitems, expgroup.clients))
        dataitems_concat = list(concat(dataitems))
        dataitems_with_client = []
        for ditem in dataitems_concat:
            dataitem = ditem.as_dict()
            di_and_client = assoc(dataitem, 'client', ditem.client.as_dict())
            dataitems_with_client.append(di_and_client)
        experimentgroup = expgroup.as_dict()
        resultwithconf = assoc(experimentgroup, 'configurations', configurations)
        resultwithclient = assoc(resultwithconf, 'clients', clients)
        result = assoc(resultwithclient, 'dataitems', dataitems_with_client)

        return result

    @view_config(route_name='experimentgroup', request_method="DELETE")
    def experimentgroup_DELETE(self):
        """ Delete one experimentgroup """
        expgroupid = self.request.swagger_data['expgroupid']
        experimentgroup = ExperimentGroup.get(expgroupid)
        expid = self.request.swagger_data['expid']
        if not experimentgroup or experimentgroup.experiment.id != expid:
            print_log(datetime.datetime.now(), 'DELETE',
                      '/experiments/' + str(expid) + '/experimentgroups/' + str(expgroupid),
                      'Delete experimentgroup', 'Failed')
            return self.createResponse(None, 400)
        ExperimentGroup.destroy(experimentgroup)
        print_log(datetime.datetime.now(), 'DELETE',
                  '/experiments/' + str(expid) + '/experimentgroups/' + str(expgroupid),
                  'Delete experimentgroup', 'Succeeded')
        return {}
