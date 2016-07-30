from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from ..models import DatabaseInterface
import json
import datetime


@view_defaults(renderer='json')
class Users:
	def __init__(self, request):
		self.request = request
		self.DB = DatabaseInterface(self.request.dbsession)

	@view_config(route_name='configurations', request_method="OPTIONS")
	def configurations_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
		res.headers.add('Access-Control-Allow-Headers', 'username')
		return res

	#5 List configurations for specific user
	@view_config(route_name='configurations', request_method="GET")
	def configurations_GET(self):
	#Also adds the user to the DB if it doesn't exist
		username = self.request.headers.get('username')
		user = self.DB.checkUser(username)
		self.DB.assignUserToRunningExperiments(user.id)
		confs = self.DB.getTotalConfigurationForUser(user.id)
		configurations = []
		for conf in confs:
			configurations.append({'key': conf.key, 'value': int(conf.value)})
		result = json.dumps({'data': configurations})
		headers = ()
		res = Response(result)
		res.headers.add('Access-Control-Allow-Origin', '*')
		print("%s REST method=GET, url=/configurations, action=List configurations for specific user, result=%s" % (datetime.datetime.now(), result))
		return res

	@view_config(route_name='users', request_method="OPTIONS")
	def users_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
		return res

	#6 List all users
	@view_config(route_name='users', request_method="GET")
	def users_GET(self):
		users = self.DB.getAllUsers()
		usersJSON = []
		for i in range(len(users)):
			usersJSON.append(users[i].as_dict())
		result = json.dumps({'data': usersJSON})
		headers = ()
		res = Response(result)
		res.headers.add('Access-Control-Allow-Origin', '*')
		print("%s REST method=GET, url=/users, action=List all users, result=%s" % (datetime.datetime.now(), result))
		return res

	@view_config(route_name='experiments_for_user', request_method="OPTIONS")
	def experiments_for_user_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
		return res

	#8 List all experiments for specific user 
	@view_config(route_name='experiments_for_user', request_method="GET")
	def experiments_for_user_GET(self):
		id = int(self.request.matchdict['id'])
		experiments = self.DB.getExperimentsUserParticipates(id)
		experimentsJSON = []
		for i in range(len(experiments)):
			expgroup = self.DB.getExperimentgroupForUserInExperiment(id, experiments[i].id)
			exp = experiments[i].as_dict()
			exp['experimentgroup'] = expgroup.as_dict()
			experimentsJSON.append(exp)
		result = json.dumps({'data': experimentsJSON})
		headers = ()
		res = Response(result)
		res.headers.add('Access-Control-Allow-Origin', '*')
		print("%s REST method=GET, url=/users/{id}/experiments, action=List all experiments for specific user , result=%s" % (datetime.datetime.now(), result))
		return res

	@view_config(route_name='events', request_method="OPTIONS")
	def events_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
		res.headers.add('Access-Control-Allow-Headers', 'username')
		return res

	#9 Save experiment data
	@view_config(route_name='events', request_method="POST")
	def events_POST(self):
		json = self.request.json_body
		value = int(json['value'])
		key = json['key']
		startDatetime = json['startDatetime']
		endDatetime = json['endDatetime']
		username = self.request.headers['username']
		user = self.DB.getUserByUsername(username)
		result = self.DB.createDataitem(
			{'user': user,
			'value': value,
			'key':key,
			'startDatetime':startDatetime,
			'endDatetime':endDatetime
			})
		print("%s REST method=POST, url=/events, action=Save experiment data , result=%s" % (datetime.datetime.now(), result))


	@view_config(route_name='user', request_method="OPTIONS")
	def user_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'DELETE,OPTIONS')
		return res

	#10 Delete user
	@view_config(route_name='user', request_method="DELETE")
	def user_DELETE(self):
		id = int(self.request.matchdict['id'])
		result = self.DB.deleteUser(id)
		if result:
			result = 'Succeeded'
		else:
			result = 'Failed'
		headers = ()
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		print("%s REST method=DELETE, url=/users/{id}, action=Delete user, result=%s" % (datetime.datetime.now(), result))
		return res












	