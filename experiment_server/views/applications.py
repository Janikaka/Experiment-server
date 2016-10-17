""" imports """
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from experiment_server.models.applications import Application
from experiment_server.utils.log import print_log
from .webutils import WebUtils
import datetime
from toolz import concat, assoc


@view_defaults(renderer='json')
class Applications(WebUtils):
    def __init__(self, request):
        self.request = request

    """
        CORS-options
    """
    @view_config(route_name='applications', request_method="OPTIONS")
    def all_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS, DELETE, PUT')
        return res

    @view_config(route_name='application', request_method="OPTIONS")
    def all_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS, DELETE, PUT')
        return res


    @view_config(route_name='application', request_method="GET")
    def applications_GET_one(self):
        """ Find and return one application by id with GET method """
        app_id = self.request.swagger_data['id']
        app = Application.get(app_id)
        if app is None:
            print_log(datetime.datetime.now(), 'GET', '/applications/' + str(app_id), 'Get one application', None)
            return self.createResponse(None, 400)
        return app.as_dict()

    @view_config(route_name='applications', request_method="GET")
    def applications_GET(self):
        """ List all applications with GET method """
        return list(map(lambda _: _.as_dict(), Application.all()))

    @view_config(route_name='applications', request_method="POST")
    def applications_POST(self):
        """ Create new application with POST method """
        req_app = self.request.swagger_data['application']
        app = Application(
            name=req_app.name
        )
        Application.save(app)
        print_log(req_app.name, 'POST', '/applications', 'Create new application', app)
        return app.as_dict()

    @view_config(route_name='application', request_method="DELETE")
    def applications_DELETE_one(self):
        """ Find and delete one application by id with destroy method """
        app_id = self.request.swagger_data['id']
        app = Application.get(app_id)
        if not app:
            print_log(datetime.datetime.now(), 'DELETE', '/applications/' + str(app_id), 'Delete application', 'Failed')
            return self.createResponse(None, 400)
        Application.destroy(app)
        print_log(datetime.datetime.now(), 'DELETE', '/applications/' + str(app_id), 'Delete application', 'Succeeded')
        return {}

    @view_config(route_name='configurationkeys_for_app', request_method="GET")
    def configurationkeys_for_application_GET(self):
        """ List all configurationkeys of specific application """
        app_id = self.request.swagger_data['id']
        app = Application.get(app_id)
        if app is None:
            print_log(datetime.datetime.now(), 'GET', '/applications/' + str(id) + '/configurationkeys',
                      'Get configurationkeys of one application', None)
            return self.createResponse(None, 400)
        return list(map(lambda _: _.as_dict(), app.configurationkeys))

    @view_config(route_name='rangeconstraints_for_app', request_method='GET')
    def rangeconstraints_for_app_GET(self):
        """ list all rangeconstraints of one application """
        app_id = self.request.swagger_data['id']
        app = Application.get(app_id)
        if app is None:
            print_log(datetime.datetime.now(), 'GET', '/applications/' + str(id) + '/rangeconstraints',
                      'Get rangeconstraints of one application', None)
            return self.createResponse(None, 400)
        ranges = list(map(lambda _: _.rangeconstraints, app.configurationkeys))
        ranges_concat = list(concat(ranges))

        return list(map(lambda _: _.as_dict(), ranges_concat))

    @view_config(route_name='app_data', request_method="GET")
    def data_for_app_GET(self):
        """ List all configurationkeys and rangeconstraints of specific application.
            Returns application with configurationkeys and rangeconstraints of conf.keys
        """
        app_id = self.request.swagger_data['id']
        app = Application.get(app_id)
        if app is None:
            print_log(datetime.datetime.now(), 'GET', '/applications/' + str(id) + '/rangeconstraints',
                      'Get all things of one application', None)
            return self.createResponse(None, 400)
        ranges = list(map(lambda _: _.rangeconstraints, app.configurationkeys))
        ranges_concat = list(concat(ranges))
        ranges_list = list(map(lambda _: _.as_dict(), ranges_concat))
        configurationkeys = list(map(lambda _: _.as_dict(), app.configurationkeys))
        resultwithck = assoc(app.as_dict(), 'configurationkeys', configurationkeys)

        return assoc(resultwithck, 'rangeconstraints', ranges_list)
