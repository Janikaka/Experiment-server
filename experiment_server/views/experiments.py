""" Imports """
import datetime
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from experiment_server.models import DatabaseInterface
from experiment_server.utils.log import print_log
from experiment_server.views.webutils import WebUtils

@view_defaults(renderer='json')
class Experiments(WebUtils):
    def __init__(self, request):
        self.request = request
        self.DB = DatabaseInterface(self.request.dbsession)

    @view_config(route_name='experiments', request_method="OPTIONS")
    def experiments_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS')
        return res

    @view_config(route_name='experiments', request_method="POST")
    def experiments_POST(self):
        """ Create new experiment """
        data = self.request.json_body
        name = data['name']
        experimentgroups = data['experimentgroups']
        start_datetime = data['startDatetime']
        endDatetime = data['endDatetime']
        size = int(data['size'])
        expgroups = []
        for i in range(len(experimentgroups)):
            expgroup = self.DB.create_experimentgroup({'name': experimentgroups[i]['name']})
            expgroups.append(expgroup)
            confs = experimentgroups[i]['configurations']
            for j in range(len(confs)):
                key = confs[j]['key']
                value = confs[j]['value']
                self.DB.create_configuration({'key': key,
                                              'value': value,
                                              'experimentgroup': expgroup})
        experiment = self.DB.create_experiment(
            {'name': name,
             'startDatetime': start_datetime,
             'endDatetime': endDatetime,
             'experimentgroups': expgroups,
             'size': size
            })
        if experiment is None:
            print_log(datetime.datetime.now(), 'POST', '/experiments', 'Create new experiment', None)
            return self.createResponse(None, 200)
        result = {'data': experiment.as_dict()}
        # Experimenter sends double request?!
        print_log(datetime.datetime.now(), 'POST', '/experiments', 'Create new experiment', result)
        return self.createResponse(result, 200)

    @view_config(route_name='experiments', request_method="GET")
    def experiments_GET(self):
        """ List all experiments """
        experiments = self.DB.get_all_experiments()
        experimentsJSON = []
        for i in range(len(experiments)):
            experiment = experiments[i].as_dict()
            experiment['status'] = self.DB.get_status_for_experiment(experiments[i].id)
            experimentsJSON.append(experiment)
        result = {'data': experimentsJSON}
        print_log(datetime.datetime.now(), 'GET', '/experiments', 'List all experiments', result)
        return self.createResponse(result, 200)

    @view_config(route_name='experiment_metadata', request_method="OPTIONS")
    def experiment_metadata_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return res

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

    @view_config(route_name='experiment', request_method="OPTIONS")
    def experiment_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'DELETE,OPTIONS')
        return res

    @view_config(route_name='experiment', request_method="DELETE")
    def experiment_DELETE(self):
        """ Delete experiment """
        id = int(self.request.matchdict['id'])
        result = self.DB.delete_experiment(id)
        if not result:
            print_log(datetime.datetime.now(), 'DELETE', '/experiments/' + str(id), 'Delete experiment', 'Failed')
            return self.createResponse(None, 400)
        print_log(datetime.datetime.now(), 'DELETE', '/experiments/' + str(id), 'Delete experiment', 'Succeeded')
        return self.createResponse(None, 200)

    @view_config(route_name='users_for_experiment', request_method="OPTIONS")
    def users_for_experiment_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return res

    @view_config(route_name='users_for_experiment', request_method="GET")
    def users_for_experiment_GET(self):
        """ List all users for specific experiment """
        id = int(self.request.matchdict['id'])
        users = self.DB.get_users_for_experiment(id)
        if users is None:
            print_log(datetime.datetime.now(), 'GET', '/experiments/' + str(id) + '/users',
                      'List all users for specific experiment', None)
            return self.createResponse(None, 400)
        usersJSON = []
        for i in range(len(users)):
            user = users[i].as_dict()
            experimentgroup = self.DB.get_experimentgroup_for_user_in_experiment(users[i].id, id)
            user['experimentgroup'] = experimentgroup.as_dict()
            user['totalDataitems'] = self.DB.get_total_dataitems_for_user_in_experiment(users[i].id, id)
            usersJSON.append(user)
        result = {'data': usersJSON}
        print_log(datetime.datetime.now(), 'GET', '/experiments/' + str(id) + '/users',
                  'List all users for specific experiment', result)
        return self.createResponse(result, 200)

    @view_config(route_name='experiment_data', request_method="OPTIONS")
    def experiment_data_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return res

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

    @view_config(route_name='experimentgroup', request_method="OPTIONS")
    def experimentgroup_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'GET,DELETE,OPTIONS')
        return res

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
        expgroupid = int(self.request.matchdict['expgroupid'])
        experimentgroup = self.DB.get_experimentgroup(expgroupid)
        experiment_id = experimentgroup.experiment_id
        expid = int(self.request.matchdict['expid'])
        result = self.DB.delete_experimentgroup(expgroupid)
        if not result or experiment_id != expid:
            print_log(datetime.datetime.now(), 'DELETE',
                      '/experiments/' + str(expid) + '/experimentgroups/' + str(expgroupid),
                      'Delete experimentgroup',
                      'Failed')
            return self.createResponse(None, 400)
        print_log(datetime.datetime.now(), 'DELETE',
                  '/experiments/' + str(expid) + '/experimentgroups/' + str(expgroupid),
                  'Delete experimentgroup',
                  'Succeeded')
        return self.createResponse(None, 200)

    @view_config(route_name='user_for_experiment', request_method="OPTIONS")
    def user_for_experiment_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'DELETE,OPTIONS')
        return res

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
