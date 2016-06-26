from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from ..models import DatabaseInterface


@view_defaults(renderer='json')
class Users:
	def __init__(self, request):
		self.request = request
		self.DB = DatabaseInterface(self.request.dbsession)

	#5 List configurations for specific user
	@view_config(route_name='configurations', request_method="GET")
	def configurations_GET(self):
		json = self.request.json_body
		#TODO   DOES THIS ADD THE USER TO DB IF METHOD IS CALLED THE FIRST TIME?

	#6 List all users
	@view_config(route_name='users', request_method="GET", renderer='../templates/all_users.jinja2')
	def users_GET(self):
		return {'users': self.DB.getAllUsers()}

	#8 List all experiments for specific user 
	@view_config(route_name='experiments_for_user', request_method="GET", renderer='../templates/experiments_for_user.jinja2')
	def experiments_for_user_GET(self):
		id = self.request.matchdict['id']
		return {'user': self.DB.getUser(id), 'experiments': self.DB.getExperimentsForUser(id)}

	#9 Save experiment data
	@view_config(route_name='events', request_method="POST")
	def events_POST(self):
		json = self.request.json_body
		value = json['value']
		id = None
		self.DB.createDataitem({'user': self.DB.getUser(id), 'value': value})

	#10 Delete user
	@view_config(route_name='user', request_method="DELETE")
	def user_DELETE(self):
		self.DB.deleteUser(self.request.matchdict['id'])
	













	