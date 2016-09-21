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

    @view_config(route_name='application', request_method="GET")
    def applications_GET_one(self):
        """ Find and return one application by id with GET method """
        app_id = int(self.request.matchdict['id'])
        application =self.DB.get_application_by_id(app_id)
        result = {'data': application.as_dict()}
        print_log(datetime.datetime.now(), 'GET', '/applications/{id}', 'Get one application', result)
        return self.createResponse(result, 200)

    @view_config(route_name='applications', request_method="GET")
    def applications_GET(self):
        """ List all applications with GET method """
        applications = self.DB.get_all_applications()
        applicationsJSON = []
        for i in range(len(applications)):
            applicationsJSON.append(applications[i].as_dict())
        result = {'data': applicationsJSON}
        print_log(datetime.datetime.now(), 'GET', '/applications', 'List all applications', result)
        return self.createResponse(result, 200)

    @view_config(route_name='applications', request_method="POST")
    def applications_POST(self):
        """ Create new application with POST method """
        data = self.request.json_body
        name = data['name']

        application = self.DB.create_application(
            {
                'name': name
            })

        result = {'data': application.as_dict()}
        print_log(name,'POST','/applications', 'Create new application', result)
        return self.createResponse(result, 200)
