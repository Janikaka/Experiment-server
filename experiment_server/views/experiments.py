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
			expgroup = self.DB.createExperimentgroup({'name': experimentgroups[i].experimentgroup})
			expgroups.append(expgroup)
			confKey = experimentgroups[i].confKey
			confValue = experimentgroups[i].confValue
			self.DB.createConfiguration({'key':confKey, 'value':confValue, 'experimentgroup':expgroup})
		self.DB.createExperiment({'name':name, 'experimentgroups':expgroups});
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		print(res)
		return res

	#2 List all experiments
	@view_config(route_name='experiments', request_method="GET", renderer='../templates/all_experiments.jinja2')
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
		print(res)
		return res

	#3 Show specific experiment metadata
	@view_config(route_name='experiment_metadata', request_method="GET")
	def experiment_metadata_GET(self):
		id = self.request.matchdict['id']
		experiment = self.DB.getExperiment(id)
		output = json.dumps({'data': {'name': experiment.name, 'id': experiment.id, 'experimentgroups': experiment.experimentgroups}})
		headers = ()
		res = Response(output)
		res.headers.add('Access-Control-Allow-Origin', '*')
		print(res)
		return res

	#4 Delete experiment
	@view_config(route_name='experiment', request_method="DELETE")
	def experiment_DELETE(self):
		self.DB.deleteExperiment(self.request.matchdict['id'])

	#7 List all users for specific experiment
	@view_config(route_name='users_for_experiment', request_method="GET")
	def users_for_experiment_GET(self):
		id = self.request.matchdict['id']
		users = self.DB.getUsersInExperiment(id)
		usersJSON = []
		for i in range(len(users)):
			user = {"id":users[i].id, "username":users[i].username}
			usersJSON.append(user)
		output = json.dumps({'data': usersJSON})
		headers = ()
		res = Response(output)
		res.headers.add('Access-Control-Allow-Origin', '*')
		print(res)
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
