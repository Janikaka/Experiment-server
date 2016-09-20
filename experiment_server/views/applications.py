from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from ..models import DatabaseInterface
import datetime
from experiment_server.utils.log import print_log
from .webutils import WebUtils


@view_defaults(renderer='json')
class Applications(WebUtils):
    def __init__(self, request):
        self.request = request
        self.DB = DatabaseInterface(self.request.dbsession)

    @view_config(route_name='applications', request_method="OPTIONS")
    def applications_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return res

    @view_config(route_name='applications', request_method="GET")
    def applications_GET(self):
        """ List all applications in route /applications """
        applications = self.DB.get_all_applications()
        applicationsJSON = []
        for i in range(len(applications)):
            applicationsJSON.append(applications[i].as_dict())
        result = {'data': applicationsJSON}
        print_log(datetime.datetime.now(), 'GET', '/applications', 'List all applications', result)
        return self.createResponse(result, 200)
