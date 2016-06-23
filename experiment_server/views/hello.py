from pyramid.view import view_config, view_defaults

from pyramid.response import Response

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






#curl -H "Content-Type: application/json" -X POST -d '{"username":"xyz","password":"xyz"}' http://0.0.0.0:6543/hello/123

#curl -H "Content-Type: application/json" -H "hedari: todella paha" -X POST -d '{"username":"xyz","password":"xyz"}' http://0.0.0.0:6543/hello/123