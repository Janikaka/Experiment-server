""" Imports """
import datetime
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from experiment_server.models import DatabaseInterface
from experiment_server.utils.log import print_log
from experiment_server.views.webutils import WebUtils

from experiment_server.models.experiments import Experiment
from experiment_server.models.experimentgroups import ExperimentGroup

@view_defaults(renderer='json')
class Experiments(WebUtils):
    def __init__(self, request):
        self.request = request
        self.DB = DatabaseInterface(self.request.dbsession)

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
        return list(map(lambda _: _.as_dict(), Experiment.all()))

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
        """ Delete experiment """
        exp_id = self.request.swagger_data['id']
        exp = Experiment.get(exp_id)
        if not exp:
            print_log(datetime.datetime.now(), 'DELETE', '/experiments/' + str(exp_id), 'Delete experiment', 'Failed')
            return self.createResponse(None, 400)
        Experiment.destroy(exp)
        print_log(datetime.datetime.now(), 'DELETE', '/experiments/' + str(exp_id), 'Delete experiment', 'Succeeded')
        return self.createResponse(None, 200)

    @view_config(route_name='experiment_metadata', request_method="GET")
    def experiment_metadata_GET(self):
        """ Show specific experiment metadata """
        id = int(self.request.matchdict['id'])
        experiment = self.DB.get_experiment(id)
        if experiment is None:
            print_log(datetime.datetime.now(), 'GET', '/experiments/' + str(id) + '/metadata',
                      'Show specific experiment metadata', None)
            return self.createResponse(None, 400)
        experimentAsJSON = experiment.as_dict()
        totalDataitems = self.DB.get_total_dataitems_for_experiment(id)
        experimentgroups = []
        for i in range(len(experiment.experimentgroups)):
            expgroup = experiment.experimentgroups[i]
            expgroupAsJSON = expgroup.as_dict()
            totalDataitemsForExpgroup = self.DB.get_total_dataitems_for_expgroup(expgroup.id)
            confs = expgroup.configurations
            users = []
            for i in range(len(expgroup.users)):
                users.append(expgroup.users[i].as_dict())
            configurations = []
            for i in range(len(confs)):
                configurations.append(confs[i].as_dict())
            expgroupAsJSON['configurations'] = configurations
            expgroupAsJSON['users'] = users
            experimentgroups.append(expgroupAsJSON)
        experimentAsJSON['experimentgroups'] = experimentgroups
        experimentAsJSON['totalDataitems'] = totalDataitems
        experimentAsJSON['status'] = self.DB.get_status_for_experiment(experiment.id)
        result = {'data': experimentAsJSON}
        print_log(datetime.datetime.now(), 'GET', '/experiments/' + str(id) + '/metadata',
                  'Show specific experiment metadata', result)
        return self.createResponse(result, 200)


    @view_config(route_name='users_for_experiment', request_method="GET")
    def users_for_experiment_GET(self):
        """ List all users for specific experiment """
        id = self.request.swagger_data['id']
        exp = Experiment.get(id)
        if exp is None:
            print_log(datetime.datetime.now(), 'GET', '/experiments/' + str(id) + '/users',
                      'List all users for specific experiment', None)
            return self.createResponse(None, 400)
        users=[]
        for expgroup in exp.experimentgroups:
            users.extend(map(lambda _: _.as_dict(), expgroup.users))
        return list(users)

    @view_config(route_name='experiment_data', request_method="GET")
    def experiment_data_GET(self):
        """ Show experiment data """
        expId = int(self.request.matchdict['id'])
        experiment = self.DB.get_experiment(expId)
        expgroups = experiment.experimentgroups
        experimentAsJSON = experiment.as_dict()
        experimentgroups = []
        for expgroup in expgroups:

            experimentgroup = expgroup.as_dict()
            users = []
            for user in expgroup.users:
                userAsJSON = user.as_dict()
                dataitemsForUser = []
                for dataitem in self.DB.get_dataitems_for_user_in_experiment(user.id, expId):
                    dataitemsForUser.append(dataitem.as_dict())
                userAsJSON['dataitems'] = dataitemsForUser
                users.append(userAsJSON)

            experimentgroup['users'] = users
            experimentgroups.append(experimentgroup)
        result = {'data': {'experiment': experimentAsJSON, 'experimentgroups': experimentgroups}}
        print_log(datetime.datetime.now(), 'GET',
                  '/experiments/' + str(id) + '/data', 'Show specific experiment data',
                  result)
        return self.createResponse(result, 200)

    @view_config(route_name='experimentgroup', request_method="GET")
    def experimentgroup_GET(self):
        """ Show specific experiment group metadata """
        expgroupid = int(self.request.matchdict['expgroupid'])
        expid = int(self.request.matchdict['expid'])
        expgroup = self.DB.get_experimentgroup(expgroupid)
        if expgroup is None or expgroup.experiment.id != expid:
            print_log(datetime.datetime.now(), 'GET',
                      '/experiments/' + str(expid) + '/experimentgroups/' + str(expgroupid),
                      'Show specific experimentgroup metadata', None)
            return self.createResponse(None, 400)
        confs = expgroup.configurations
        configurations = []
        for i in range(len(confs)):
            configurations.append(confs[i].as_dict())
        users = []
        for i in range(len(expgroup.users)):
            users.append(expgroup.users[i].as_dict())
        experimentgroup = expgroup.as_dict()
        experimentgroup['configurations'] = configurations
        experimentgroup['users'] = users
        experimentgroup['totalDataitems'] = self.DB.get_total_dataitems_for_expgroup(expgroup.id)
        result = {'data': experimentgroup}
        print_log(datetime.datetime.now(), 'GET',
                  '/experiments/' + str(expid) + '/experimentgroups/' + str(expgroupid),
                  'Show specific experimentgroup metadata', result)
        return self.createResponse(result, 200)

    @view_config(route_name='experimentgroup', request_method="DELETE")
    def experimentgroup_DELETE(self):
        """ Delete experimentgroup """
        expgroupid = self.request.swagger_data['expgroupid']
        experimentgroup = ExperimentGroup.get(expgroupid)
        expid = self.request.swagger_data['expid']
        if not experimentgroup:
            print_log(datetime.datetime.now(), 'DELETE',
                      '/experiments/' + str(expid) + '/experimentgroups/' + str(expgroupid),
                      'Delete experimentgroup', 'Failed')
            return self.createResponse(None, 400)
        ExperimentGroup.destroy(experimentgroup)
        print_log(datetime.datetime.now(), 'DELETE',
                  '/experiments/' + str(expid) + '/experimentgroups/' + str(expgroupid),
                  'Delete experimentgroup', 'Succeeded')
        return self.createResponse(None, 200)

    @view_config(route_name='user_for_experiment', request_method="DELETE")
    def user_for_experiment_DELETE(self):
        """ Delete user from specific experiment """
        expid = int(self.request.matchdict['expid'])
        userid = int(self.request.matchdict['userid'])
        result = self.DB.delete_user_from_experiment(userid, expid)
        if not result:
            print_log(datetime.datetime.now(),
                      'GET', '/experiments/' + str(expid) + '/users/' + str(userid),
                      'Delete user from specific experiment', 'Failed')
            return self.createResponse(None, 400)
        print_log(datetime.datetime.now(), 'GET', '/experiments/' + str(expid) + '/users/' + str(userid),
                  'Delete user from specific experiment', 'Succeeded')
        return self.createResponse(None, 200)
