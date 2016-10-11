from pyramid.view import view_config, view_defaults

from .webutils import WebUtils

@view_defaults(renderer='json')
class Index(WebUtils):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='index', request_method="GET")
    def GET_API_data(self):
        return {"version": "0.1", "description": "Experiment API for various experiment configurations"}
