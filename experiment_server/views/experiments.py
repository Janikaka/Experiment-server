import datetime
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from experiment_server.utils.log import print_log
from experiment_server.views.webutils import WebUtils

from experiment_server.models.applications import Application
from experiment_server.models.clients import Client
from experiment_server.models.experiments import Experiment
from experiment_server.models.experimentgroups import ExperimentGroup

from toolz import assoc, concat

@view_defaults(renderer='json')
class Experiments(WebUtils):
    #TODO: POST experimentgroups: create new experimentgroup

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
        app_id = self.request.swagger_data['appid']
        req_exp = self.request.swagger_data['experiment']
        exp = Experiment(
                name=req_exp.name,
                startDatetime = req_exp.startDatetime,
                endDatetime = req_exp.endDatetime,
                application_id = app_id
        )

        Experiment.save(exp)
        print_log(req_exp.name, 'POST', '/experiments', 'Create new experiment', exp)
        return exp.as_dict()

    @view_config(route_name='experiments', request_method="GET")
    def experiments_GET(self):
        """ List all Application's Experiments including Experiments' status """
        app_id = self.request.swagger_data['appid']
        experiments = Experiment.query().join(Application)\
            .filter(Application.id == app_id).all()

        return list(map(lambda _: assoc(_.as_dict(), 'status',\
            _.get_status()), experiments))

    @view_config(route_name='experiment', request_method="GET", renderer='json')
    def experiments_GET_one(self):
        """ Find and return one Application's Experiment by id with GET method """
        app_id = self.request.swagger_data['appid']
        exp_id = self.request.swagger_data['expid']
        exp = Experiment.query().join(Application)\
            .filter(Application.id == app_id, Experiment.id == exp_id).one_or_none()
        if exp is None:
            print_log(datetime.datetime.now(), 'GET',\
                '/applications/%s/experiments/%s' % (app_id, exp_id),\
                'Get one experiment', 'Failed')
            return self.createResponse(None, 400)
        exp_dict = exp.as_dict()
        exp_dict['status'] = exp.get_status()

        return exp_dict

    @view_config(route_name='experiment', request_method="DELETE")
    def experiment_DELETE(self):
        """ Delete one experiment """
        app_id = self.request.swagger_data['appid']
        exp_id = self.request.swagger_data['expid']
        log_address = '/applications/%s/experiments/%s' % (app_id, exp_id)

        exp = Experiment.query().join(Application)\
            .filter(Application.id == app_id, Experiment.id == exp_id)\
            .one_or_none()
        if exp is None:
            print_log(datetime.datetime.now(), 'DELETE', log_address,\
                'Delete experiment', 'Failed')
            return self.createResponse(None, 400)

        Experiment.destroy(exp)
        print_log(datetime.datetime.now(), 'DELETE', log_address,\
            'Delete experiment', 'Succeeded')
        return {}

    @view_config(route_name='clients_for_experiment', request_method="GET")
    def clients_for_experiment_GET(self):
        """ List all clients for specific experiment """
        app_id = self.request.swagger_data['appid']
        exp_id = self.request.swagger_data['expid']
        exp = Experiment.query().join(Application)\
            .filter(Experiment.id == exp_id, Application.id == app_id)\
            .one_or_none()

        if exp == None:
            print_log(datetime.datetime.now(), 'GET', '/experiments/' + str(id) + '/clients',
                      'List all clients for specific experiment', 'Failed')
            return self.createResponse(None, 400)

        clients = Client.query()\
            .join(Client.experimentgroups, Experiment, Application)\
            .filter(Experiment.id == exp_id, Application.id == app_id).all()
        return list(map(lambda _: _.as_dict(), clients))

    @view_config(route_name='experimentgroups', request_method="GET")
    def experimentgroup_GET(self):
        app_id = self.request.swagger_data['appid']
        exp_id = self.request.swagger_data['expid']
        experiment = Experiment.query().join(Application)\
            .filter(Application.id == app_id, Experiment.id == exp_id)\
            .one_or_none()

        if experiment == None:
            print_log(datetime.datetime.now(), 'GET', \
                '/applications/%s/experiments/%s/experimentgroups' % ((app_id, exp_id)),
                      'List all ExperimentGroups for specific experiment', 'Failed')
            return self.createResponse(None, 400)

        experimentgroups = ExperimentGroup.query().filter(ExperimentGroup.experiment_id == experiment.id)

        return list(map(lambda _: _.as_dict(), experimentgroups))


    @view_config(route_name='experimentgroup', request_method="GET")
    def experimentgroup_GET_one(self):
        """ Show specific experiment group metadata """
        app_id = self.request.swagger_data['appid']
        expid = self.request.swagger_data['expid']
        expgroupid = self.request.swagger_data['expgroupid']

        #expgroup = ExperimentGroup.get(expgroupid)
        expgroup = ExperimentGroup.query().join(Experiment, Application)\
            .filter(ExperimentGroup.id == expgroupid, Experiment.id == expid,\
                Application.id == app_id)\
            .one_or_none()

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
        app_id = self.request.swagger_data['appid']
        exp_id = self.request.swagger_data['expid']
        expgroupid = self.request.swagger_data['expgroupid']

        experimentgroup = ExperimentGroup.get(expgroupid)
        experimentgroup = ExperimentGroup.query().join(Experiment, Application)\
            .filter(ExperimentGroup.id == expgroupid, Experiment.id == exp_id,\
                Application.id == app_id)\
            .one_or_none()

        log_address = '/applications/%s/experiments/%s/experimentgroups/%s'\
            % (app_id, exp_id, expgroupid)

        if not experimentgroup or experimentgroup.experiment.id != exp_id:
            print_log(datetime.datetime.now(), 'DELETE',
                      log_address,
                      'Delete experimentgroup', 'Failed')
            return self.createResponse(None, 400)
        ExperimentGroup.destroy(experimentgroup)
        print_log(datetime.datetime.now(), 'DELETE',
                  log_address,
                  'Delete experimentgroup', 'Succeeded')
        return {}
