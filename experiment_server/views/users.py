from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from ..models import DatabaseInterface
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

	# List configurations for specific user
	@view_config(route_name='configurations', request_method="GET")
	def configurations_GET(self):
	#Also adds the user to the DB if doesn't exist
		username = self.request.headers.get('username')
		user = self.DB.checkUser(username)
		if user is None:
			printLog(datetime.datetime.now(), 'GET', '/configurations', 'List configurations for specific user', None)
			return createResponse(None, 400)
		self.DB.assignUserToRunningExperiments(user.id)
		confs = self.DB.getTotalConfigurationForUser(user.id)
		configurations = []
		for conf in confs:
			configurations.append({'key': conf.key, 'value': conf.value})
		result = {'data': configurations}
		printLog(datetime.datetime.now(), 'GET', '/configurations', 'List configurations for specific user', result)
		return createResponse(result, 200)

	@view_config(route_name='users', request_method="OPTIONS")
	def users_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
		return res

	# List all users
	@view_config(route_name='users', request_method="GET")
	def users_GET(self):
		users = self.DB.getAllUsers()
		usersJSON = []
		for i in range(len(users)):
			usersJSON.append(users[i].as_dict())
		result = {'data': usersJSON}
		printLog(datetime.datetime.now(), 'GET', '/users', 'List all users', result)
		return createResponse(result, 200)

	@view_config(route_name='experiments_for_user', request_method="OPTIONS")
	def experiments_for_user_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
		return res

	# List all experiments for specific user 
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
		result = {'data': experimentsJSON}
		printLog(datetime.datetime.now(), 'GET', '/users/' + str(id) + '/experiments', 'List all experiments for specific user', result)
		return createResponse(result, 200)

	@view_config(route_name='events', request_method="OPTIONS")
	def events_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
		res.headers.add('Access-Control-Allow-Headers', 'username')
		return res

	# Save experiment data
	@view_config(route_name='events', request_method="POST")
	def events_POST(self):
		json = self.request.json_body
		value = int(json['value'])
		key = json['key']
		startDatetime = json['startDatetime']
		endDatetime = json['endDatetime']
		username = self.request.headers['username']
		user = self.DB.getUserByUsername(username)
		if user is None:
			printLog(datetime.datetime.now(), 'POST', '/events', 'Save experiment data', None)
			return createResponse(None, 400)
		result = {'data': self.DB.createDataitem(
			{'user': user,
			'value': value,
			'key':key,
			'startDatetime':startDatetime,
			'endDatetime':endDatetime
			}).as_dict()}
		printLog(datetime.datetime.now(), 'POST', '/events', 'Save experiment data', result)
		return createResponse(result, 200)

	@view_config(route_name='user', request_method="OPTIONS")
	def user_OPTIONS(self):
		res = Response()
		res.headers.add('Access-Control-Allow-Origin', '*')
		res.headers.add('Access-Control-Allow-Methods', 'DELETE,OPTIONS')
		return res

	# Delete user
	@view_config(route_name='user', request_method="DELETE")
	def user_DELETE(self):
		id = int(self.request.matchdict['id'])
		result = self.DB.deleteUser(id)
		if not result:
			printLog(datetime.datetime.now(), 'DELETE', '/users/' + str(id), 'Delete user', 'Failed')
			return createResponse(None, 400)
		printLog(datetime.datetime.now(), 'DELETE', '/users/' + str(id), 'Delete user', 'Succeeded')
		return createResponse(None, 200)












	