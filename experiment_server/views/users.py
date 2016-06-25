from pyramid.view import view_config, view_defaults

from pyramid.response import Response


@view_defaults(renderer='json')
class Users:
	def __init__(self, request):
		self.request = request

	#6 List all users
	@view_config(route_name='users', request_method="GET")
	def users_GET(self):
		return None

	#8 List all experiments for specific user 
	@view_config(route_name='experiments_for_user', request_method="GET")
	def experiments_for_user_GET(self):
		return None

	#10 Delete user
	@view_config(route_name='user', request_method="DELETE")
	def user_DELETE(self):
		return None

	#9 Save experiment data
	@view_config(route_name='events', request_method="POST")
	def events_POST(self):
		return None

	#5 List configurations for specific user
	@view_config(route_name='configurations', request_method="GET")
	def configurations_GET(self):
		return None













	