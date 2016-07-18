from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from ..models import DatabaseInterface
from pyramid.httpexceptions import HTTPFound
import json
from datetime import datetime


@view_defaults(renderer='json')
class Experiments:
	def __init__(self, request):
		self.request = request
		self.DB = DatabaseInterface(self.request.dbsession)
#2016-07-18 18:35:21
	#1 Create new experiment
	@view_config(route_name='experiments', request_method="POST")
	def experiments_POST(self):
		data = self.request.json_body
		name = data['name']
		experimentgroups = data['experimentgroups']
		startDatetime = datetime.strptime(data['startDatetime'], "%Y-%m-%d %H:%M:%S")
		endDatetime = datetime.strptime(data['endDatetime'], "%Y-%m-%d %H:%M:%S")
		expgroups = []
		for i in range(len(experimentgroups)):
			expgroup = self.DB.createExperimentgroup({'name': experimentgroups[i]['name']})
			expgroups.append(expgroup)
			confs = experimentgroups[i]['configurations']
			for j in range(len(confs)):
				key = confs[j]['key']
				value = confs[j]['value']
				self.DB.createConfiguration({'key':key, 'value':value, 'experimentgroup':expgroup})
		self.DB.createExperiment(
			{'name':name, 
			'startDatetime':startDatetime,
			'endDatetime':endDatetime,
			'experimentgroups':expgroups
			});
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		print(res)
		return res

	#2 List all experiments
	@view_config(route_name='experiments', request_method="GET")
	def experiments_GET(self):
		experiments = self.DB.getAllExperiments()
		experimentsJSON = []
		for i in range(len(experiments)):
			exp = {"id":experiments[i].id, "name": experiments[i].name}
			experimentsJSON.append(exp)
		output = json.dumps({'data': experimentsJSON})
		headers = ()
		res = Response(output)
		res.headers.add('Access-Control-Allow-Origin', '*')
		return res

	#3 Show specific experiment metadata
	@view_config(route_name='experiment_metadata', request_method="GET")
	def experiment_metadata_GET(self):
		id = self.request.matchdict['id']
		experiment = self.DB.getExperiment(id)
		totalDataitems = self.DB.getTotalDataitemsForExperiment(id)
		experimentgroups = []
		for i in range(len(experiment.experimentgroups)):
			expgroup = experiment.experimentgroups[i]
			totalDataitemsForExpgroup = self.DB.getTotalDataitemsForExpgroup(expgroup.id)
			confs = expgroup.configurations
			users = []
			for i in range(len(expgroup.users)):
				users.append({'id':expgroup.users[i].id, 'username':expgroup.users[i].username})
			configurations = []
			for i in range(len(confs)):
				configurations.append({'id':confs[i].id, 'key':confs[i].key, 'value':confs[i].value})
			experimentgroups.append(
				{'id':expgroup.id, 
				'name':expgroup.name, 
				'configurations':configurations, 
				'users': users,
				'totalDataitems':totalDataitemsForExpgroup
				})
		output = json.dumps(
			{'data': 
				{'id': experiment.id, 
				'name': experiment.name, 
				'startDatetime': str(experiment.startDatetime),
				'endDatetime': str(experiment.endDatetime),
				'experimentgroups': experimentgroups,
				'totalDataitems': totalDataitems
				}
			})
		headers = ()
		res = Response(output)
		res.headers.add('Access-Control-Allow-Origin', '*')
		return res

	@view_config(route_name='experiment', request_method="OPTIONS")
	def experiment_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'POST,DELETE,OPTIONS')
		return res

	#4 Delete experiment
	@view_config(route_name='experiment', request_method="DELETE")
	def experiment_DELETE(self):
		self.DB.deleteExperiment(self.request.matchdict['id'])
		headers = ()
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		return res

	#7 List all users for specific experiment
	@view_config(route_name='users_for_experiment', request_method="GET")
	def users_for_experiment_GET(self):
		id = self.request.matchdict['id']
		id = int(id)
		users = self.DB.getUsersInExperiment(id)
		usersJSON = []
		for i in range(len(users)):
			experimentgroup = self.DB.getExperimentgroupForUserInExperiment(users[i].id, id)
			expgroup = {'id':experimentgroup.id, 'name':experimentgroup.name}
			user = {'id':users[i].id, 'username':users[i].username, 'experimentgroup':expgroup}
			usersJSON.append(user)
		output = json.dumps({'data': usersJSON})
		headers = ()
		res = Response(output)
		res.headers.add('Access-Control-Allow-Origin', '*')
		return res

	# Delete user from specific experiment
	@view_config(route_name='user_for_experiment', request_method="DELETE")
	def user_for_experiment_DELETE(self):
		print("DELETEEEEEEE")
		experimentId = int(self.request.matchdict['expid'])
		userId = int(self.request.matchdict['userid'])
		print("experimentId %d" %experimentId)
		print("userId %d" %userId)
		self.DB.deleteUserFromExperiment(userId, experimentId)
		headers = ()
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		return res

	@view_config(route_name='user_for_experiment', request_method="OPTIONS")
	def experiment_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'DELETE,OPTIONS')
		return res

	#11 Show experiment data
	@view_config(route_name='experiment_data', request_method="GET")
	def experiment_data_GET(self):
		experimentId = self.request.matchdict['id']
		experimentgroups = self.DB.getExperimentgroups(experimentId)
		dataInGroups = {'experimentgroups': []}
		for experimentgroup in experimentgroups:
			users = self.DB.getUsersInExperimentgroup(experimentgroup.id)
			usersData = []
			for user in users:
				userData = {'user':user.id, 'dataValues': []}
				dataitems = self.DB.getDataitemsForUser(user.id)
				for dataitem in dataitems:
					userData['dataValues'].append(dataitem.value)
				usersData.append(userData)
			expgroup = {'experimentgroup': {'id': experimentgroup.id, 'name': experimentgroup.name}, 'users': usersData}
			dataInGroups['experimentgroups'].append(expgroup)

		return {'dataInGroups': dataInGroups}
