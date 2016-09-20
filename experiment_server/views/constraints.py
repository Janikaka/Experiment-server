from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from ..models import DatabaseInterface
import datetime
from experiment_server.utils.log import print_log
from .webutils import WebUtils

@view_defaults(renderer='json')
class Constraints(WebUtils):
    def __init__(self, request):
        self.request = request
        self.DB = DatabaseInterface(self.request.dbsession)

    @view_config(route_name='constraints', request_method="OPTIONS")
    def constraints_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return res

    @view_config(route_name='constraints', request_method="GET")
    def constraints_GET(self):
        """ List all constraints in route /constraints"""
        constraints = self.DB.get_all_constraints()
        constraintsJSON = []
        for i in range(len(constraints)):
            constraintsJSON.append(constraints[i].as_dict())
        result = {'data': constraintsJSON}
        print_log(datetime.datetime.now(), 'GET', '/constraints', 'List all constraints', result)
        return self.createResponse(result, 200)