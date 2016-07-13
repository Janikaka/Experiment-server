from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from ..models import DatabaseInterface
from pyramid.httpexceptions import HTTPFound
import json


@view_defaults(renderer='json')
class Experiments:
	def __init__(self, request):
		self.request = request
		self.DB = DatabaseInterface(self.request.dbsession)

	#1 Create new experiment
	@view_config(route_name='experiments', request_method="POST")
	def experiments_POST(self):
		data = self.request.json_body
		name = data['name']
		experimentgroups = data['experimentgroups']
		expgroups = []
		for i in range(len(experimentgroups)):
			expgroup = self.DB.createExperimentgroup({'name': experimentgroups[i]['name']})
			expgroups.append(expgroup)
			confs = experimentgroups[i]['configurations']
			for j in range(len(confs)):
				key = confs[j]['key']
				value = confs[j]['value']
				self.DB.createConfiguration({'key':key, 'value':value, 'experimentgroup':expgroup})
		self.DB.createExperiment({'name':name, 'experimentgroups':expgroups});
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
		experimentgroups = []
		for i in range(len(experiment.experimentgroups)):
			expgroup = experiment.experimentgroups[i]
			confs = expgroup.configurations
			configurations = []
			for i in range(len(confs)):
				configurations.append({'id':confs[i].id, 'key':confs[i].key, 'value':confs[i].value})
			experimentgroups.append({'id':expgroup.id, 'name':expgroup.name, 'configurations':configurations})
		output = json.dumps({'data': {'id': experiment.id, 'name': experiment.name, 'experimentgroups': experimentgroups}})
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
		print(res)
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
