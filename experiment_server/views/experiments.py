from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from ..models import DatabaseInterface
from pyramid.httpexceptions import HTTPFound
import json
import datetime

def printLog(timestamp, method, url, action, result):
	print("%s REST method=%s, url=%s, action=%s, result=%s" % (timestamp, method, url, action, result))

def createResponse(output, status_code):
	outputJson = json.dumps(output)
	headers = ()
	res = Response(outputJson)
	res.status_code = status_code
	res.headers.add('Access-Control-Allow-Origin', '*')
	return res

@view_defaults(renderer='json')
class Experiments:
	def __init__(self, request):
		self.request = request
		self.DB = DatabaseInterface(self.request.dbsession)

	@view_config(route_name='experiments', request_method="OPTIONS")
	def experiments_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS')
		return res

	#1 Create new experiment
	@view_config(route_name='experiments', request_method="POST")
	def experiments_POST(self):
		data = self.request.json_body
		name = data['name']
		experimentgroups = data['experimentgroups']
		startDatetime = data['startDatetime']
		endDatetime = data['endDatetime']
		size = int(data['size'])
		expgroups = []
		for i in range(len(experimentgroups)):
			expgroup = self.DB.createExperimentgroup({'name': experimentgroups[i]['name']})
			expgroups.append(expgroup)
			confs = experimentgroups[i]['configurations']
			for j in range(len(confs)):
				key = confs[j]['key']
				value = confs[j]['value']
				self.DB.createConfiguration({'key':key, 'value':value, 'experimentgroup':expgroup})
		experiment = self.DB.createExperiment(
			{'name': name, 
			'startDatetime': startDatetime,
			'endDatetime': endDatetime,
			'experimentgroups': expgroups,
			'size': size
			});
		if experiment is None:
			printLog(datetime.datetime.now(), 'GET', '/experiments', 'Create new experiment', None)
			return createResponse(None, 200)
		result = {'data': experiment.as_dict()}
		#Experimenter sends double request
		printLog(datetime.datetime.now(), 'GET', '/experiments', 'Create new experiment', result)
		return createResponse(result, 200)

	#2 List all experiments
	@view_config(route_name='experiments', request_method="GET")
	def experiments_GET(self):
		experiments = self.DB.getAllExperiments()
		experimentsJSON = []
		for i in range(len(experiments)):
			experiment = experiments[i].as_dict()
			experiment['status'] = self.DB.getStatusForExperiment(experiments[i].id)
			experimentsJSON.append(experiment)
		result = {'data': experimentsJSON}		
		printLog(datetime.datetime.now(), 'GET', '/experiments', 'List all experiments', result)
		return createResponse(result, 200)

	@view_config(route_name='experiment_metadata', request_method="OPTIONS")
	def experiment_metadata_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
		return res

	#3 Show specific experiment metadata
	@view_config(route_name='experiment_metadata', request_method="GET")
	def experiment_metadata_GET(self):
		id = int(self.request.matchdict['id'])
		experiment = self.DB.getExperiment(id)
		if experiment is None:
			printLog(datetime.datetime.now(), 'GET', '/experiments/' + str(id) + '/metadata', 'Show specific experiment metadata', None)
			return createResponse(None, 400)
		experimentAsJSON = experiment.as_dict()
		totalDataitems = self.DB.getTotalDataitemsForExperiment(id)
		experimentgroups = []
		for i in range(len(experiment.experimentgroups)):
			expgroup = experiment.experimentgroups[i]
			expgroupAsJSON = expgroup.as_dict()
			totalDataitemsForExpgroup = self.DB.getTotalDataitemsForExpgroup(expgroup.id)
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
		experimentAsJSON['status'] = self.DB.getStatusForExperiment(experiment.id)
		result = {'data': experimentAsJSON}
		printLog(datetime.datetime.now(), 'GET', '/experiments/' + str(id) + '/metadata', 'Show specific experiment metadata', result)
		return createResponse(result, 200)

	@view_config(route_name='experiment', request_method="OPTIONS")
	def experiment_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'DELETE,OPTIONS')
		return res

	#4 Delete experiment
	@view_config(route_name='experiment', request_method="DELETE")
	def experiment_DELETE(self):
		id = int(self.request.matchdict['id'])
		result = self.DB.deleteExperiment(id)
		if not result:
			printLog(datetime.datetime.now(), 'DELETE', '/experiments/' + str(id), 'Delete experiment', 'Failed')
			return createResponse(None, 400)
		printLog(datetime.datetime.now(), 'DELETE', '/experiments/' + str(id), 'Delete experiment', 'Succeeded')
		return createResponse(None, 200)

	@view_config(route_name='users_for_experiment', request_method="OPTIONS")
	def users_for_experiment_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
		return res

	#7 List all users for specific experiment
	@view_config(route_name='users_for_experiment', request_method="GET")
	def users_for_experiment_GET(self):
		id = int(self.request.matchdict['id'])
		users = self.DB.getUsersForExperiment(id)
		if users is None:
			printLog(datetime.datetime.now(), 'GET', '/experiments/' + str(id) + '/users', 'List all users for specific experiment', None)
			return createResponse(None, 400)
		usersJSON = []
		for i in range(len(users)):
			user = users[i].as_dict()
			experimentgroup = self.DB.getExperimentgroupForUserInExperiment(users[i].id, id)
			user['experimentgroup'] = experimentgroup.as_dict()
			user['totalDataitems'] = self.DB.getTotalDataitemsForUserInExperiment(users[i].id, id)
			usersJSON.append(user)
		result = {'data': usersJSON}
		printLog(datetime.datetime.now(), 'GET', '/experiments/' + str(id) + '/users', 'List all users for specific experiment', result)
		return createResponse(result, 200)

	@view_config(route_name='experiment_data', request_method="OPTIONS")
	def experiment_data_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
		return res

	#11 Show specific experiment data
	@view_config(route_name='experiment_data', request_method="GET")
	def experiment_data_GET(self):
		expId = int(self.request.matchdict['id'])
		experiment = self.DB.getExperiment(expId)
		expgroups = experiment.experimentgroups
		experimentAsJSON = experiment.as_dict()
		experimentgroups = []
		for expgroup in expgroups:

			experimentgroup = expgroup.as_dict()
			dataitemsForExpgroup = []
			for dataitem in self.DB.getDataitemsForExperimentgroup(expgroup.id):
				dataitemsForExpgroup.append(dataitem.as_dict())
			experimentgroup['dataitems'] = dataitemsForExpgroup

			users = []
			for user in expgroup.users:
				userAsJSON = user.as_dict()
				dataitemsForUser = []
				for dataitem in self.DB.getDataitemsForUserInExperiment(user.id, expId):
					dataitemsForUser.append(dataitem.as_dict())
				userAsJSON['dataitems'] = dataitemsForUser
				users.append(userAsJSON)

			experimentgroup['users'] = users
			experimentgroups.append(experimentgroup)
		dataitemsForExperiment = []
		for dataitem in self.DB.getDataitemsForExperiment(expId):
			dataitemsForExperiment.append(dataitem.as_dict())
		result = {'data': {'experiment': experimentAsJSON, 'dataitems': dataitemsForExperiment,
		'experimentgroups': experimentgroups}}
		printLog(datetime.datetime.now(), 'GET', '/experiments/' + str(id) + '/data', 'Show specific experiment data', result)
		return result

	@view_config(route_name='experimentgroup', request_method="OPTIONS")
	def experimentgroup_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'GET,DELETE,OPTIONS')
		return res

	#13 Show specific experimentgroup metadata
	@view_config(route_name='experimentgroup', request_method="GET")
	def experimentgroup_GET(self):
		expgroupid = int(self.request.matchdict['expgroupid'])
		expid = int(self.request.matchdict['expid'])
		expgroup = self.DB.getExperimentgroup(expgroupid)
		if expgroup is None or expgroup.experiment.id != expid:
			printLog(datetime.datetime.now(), 'GET', '/experiments/' + str(expid) + '/experimentgroups/' + str(expgroupid), 'Show specific experimentgroup metadata', None)
			return createResponse(None, 400)
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
		experimentgroup['totalDataitems'] = self.DB.getTotalDataitemsForExpgroup(expgroup.id)
		result = {'data': experimentgroup}
		printLog(datetime.datetime.now(), 'GET', '/experiments/' + str(expid) + '/experimentgroups/' + str(expgroupid), 'Show specific experimentgroup metadata', result)
		return createResponse(result, 200)

	#12 Delete experimentgroup
	@view_config(route_name='experimentgroup', request_method="DELETE")
	def experimentgroup_DELETE(self):
		expgroupid = int(self.request.matchdict['expgroupid'])
		experimentgroup = self.DB.getExperimentgroup(expgroupid)
		experiment_id = experimentgroup.experiment_id
		expid = int(self.request.matchdict['expid'])
		result = self.DB.deleteExperimentgroup(expgroupid)
		if not result or experiment_id != expid:
			printLog(datetime.datetime.now(), 'DELETE', '/experiments/' + str(expid) + '/experimentgroups/' + str(expgroupid), 'Delete experimentgroup', 'Failed')
			return createResponse(None, 400)
		printLog(datetime.datetime.now(), 'DELETE', '/experiments/' + str(expid) + '/experimentgroups/' + str(expgroupid), 'Delete experimentgroup', 'Succeeded')
		return createResponse(None, 200)

	@view_config(route_name='user_for_experiment', request_method="OPTIONS")
	def user_for_experiment_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'DELETE,OPTIONS')
		return res

	#14 Delete user from specific experiment
	@view_config(route_name='user_for_experiment', request_method="DELETE")
	def user_for_experiment_DELETE(self):
		expid = int(self.request.matchdict['expid'])
		userid = int(self.request.matchdict['userid'])
		result = self.DB.deleteUserFromExperiment(userid, expid)
		if not result:
			printLog(datetime.datetime.now(), 'GET', '/experiments/' + str(expid) + '/users/' + str(userid), 'Delete user from specific experiment', 'Failed')
			return createResponse(None, 400)
		printLog(datetime.datetime.now(), 'GET', '/experiments/' + str(expid) + '/users/' + str(userid), 'Delete user from specific experiment', 'Succeeded')
		return createResponse(None, 200)

