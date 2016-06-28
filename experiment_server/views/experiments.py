from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from ..models import DatabaseInterface
from pyramid.httpexceptions import HTTPFound


@view_defaults(renderer='json')
class Experiments:
	def __init__(self, request):
		self.request = request
		self.DB = DatabaseInterface(self.request.dbsession)

	@view_config(route_name='experiments_form', renderer='../templates/new_experiment.jinja2')
	def experiments_FORM(self):
		return {'url': '/experiments'}

	#1 Create new experiment
	@view_config(route_name='experiments', request_method="POST")
	def experiments_POST(self):
		#!!!! new_eperiment.jinja2 ei vielä lähetä dataa JSON-muodossa !!!!
		#Näin alkuun tukee vain kahta groupsia
		#data = self.request.json_body
		#experimentgroups = data["experimentgroups"]
		#name = data["name"]

		#Tämä on vain pikaratkaisu:
		name = self.request.params['name']
		group1 = self.request.params['group1']
		group2 = self.request.params['group2']
		experimentgroupNames = [group1, group2]
		group1Conf = {'key': self.request.params['group1key'], 'value': self.request.params['group1value']}
		group2Conf = {'key': self.request.params['group2key'], 'value': self.request.params['group2value']}
		confs = [group1Conf, group2Conf]
		experimentgroups = []
		for i in range(len(experimentgroupNames)):
			expgroup = self.DB.createExperimentgroup({'name': experimentgroupNames[i]})
			experimentgroups.append(expgroup)
			conf = confs[i]
			conf['experimentgroup'] = expgroup
			self.DB.createConfiguration(conf)
		self.DB.createExperiment({'name': name, 'experimentgroups': experimentgroups})
		return HTTPFound(location='/experiments')

	#2 List all experiments
	@view_config(route_name='experiments', request_method="GET", renderer='../templates/all_experiments.jinja2')
	def experiments_GET(self):
		return {'experiments':self.DB.getAllExperiments()}

	#3 Show specific experiment metadata
	@view_config(route_name='experiment_metadata', request_method="GET", renderer='../templates/experiment_metadata.jinja2')
	def experiment_metadata_GET(self):
		experiment = self.DB.getExperiment(self.request.matchdict['id'])
		return {'name': experiment.name, 'id': experiment.id, 'experimentgroups': experiment.experimentgroups}

	#4 Delete experiment
	@view_config(route_name='experiment', request_method="DELETE")
	def experiment_DELETE(self):
		#Browser need to refresh after deleting
		self.DB.deleteExperiment(self.request.matchdict['id'])

	#7 List all users for specific experiment
	@view_config(route_name='users_for_experiment', request_method="GET", renderer='../templates/users_in_experiment.jinja2')
	def users_for_experiment_GET(self):
		return {'users': self.DB.getUsersInExperiment(self.request.matchdict['id']), 'experiment': self.DB.getExperiment(self.request.matchdict['id'])}

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



"""
@view_defaults(renderer='json')
class Hello:
	def __init__(self, request):
		self.request = request
	@view_config(route_name='hello', request_method="GET")
	def hello_get(self):
		return dict(a=1, b=2)
	@view_config(route_name='hello', request_method="POST")
	def hello_post(self):
		json = self.request.json_body
		json["kukkuu"] = "hellurei"
		json["hedari"] = self.request.headers["hedari"]
		self.request.headers["foo"] = 3
		return json

"""
#curl -H "Content-Type: application/json" -X POST -d '{"name":"First experiment","experimentgroups":["group A", "group B"]}' http://0.0.0.0:6543/experiments

#curl -H "Content-Type: application/json" -X POST -d '{"username":"xyz","password":"xyz"}' http://0.0.0.0:6543/hello/123

#curl -H "Content-Type: application/json" -H "hedari: todella paha" -X POST -d '{"username":"xyz","password":"xyz"}' http://0.0.0.0:6543/hello/123