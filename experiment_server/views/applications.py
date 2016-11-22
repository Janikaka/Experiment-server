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

    """
        Helper functions
    """
    def get_unused_apikey(self):
        import uuid
        apikey = str(uuid.uuid4())

        while Application.get_by('apikey', apikey) is not None:
            apikey = str(uuid.uuid4())

        return apikey

    def set_app_apikey(self, application, app_id):
        apikey = self.get_unused_apikey()

        application.apikey = apikey
        Application.save(application)

        return Application.get(app_id)

    """
        Route listeners
    """

    @view_config(route_name='application', request_method="GET")
    def applications_GET_one(self):
        """ Find and return one application by id with GET method """
        app_id = self.request.swagger_data['id']
        app = Application.get(app_id)
        if app is None:
            print_log(datetime.datetime.now(), 'GET', '/applications/' + str(app_id), 'Get one application', None)
            return self.createResponse(None, 400)

        if app.apikey is None:
            app = self.set_app_apikey(app, app_id)

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
            name=req_app.name,
            apikey=self.get_unused_apikey()
        )
        Application.save(app)
        print_log(req_app.name, 'POST', '/applications', 'Create new application', app)
        return app.as_dict()

    @view_config(route_name='application', request_method="DELETE")
    def applications_DELETE_one(self):
        """ Find and delete one application by id with delete method """
        app_id = self.request.swagger_data['id']
        app = Application.get(app_id)
        if not app:
            print_log(datetime.datetime.now(), 'DELETE', '/applications/' + str(app_id), 'Delete application', 'Failed')
            return self.createResponse(None, 400)
        Application.destroy(app)
        print_log(datetime.datetime.now(), 'DELETE', '/applications/' + str(app_id), 'Delete application', 'Succeeded')
        return {}

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
        configurationkeys = app.configurationkeys
        ranges = list(concat(list(map(lambda _: _.rangeconstraints, configurationkeys))))
        app_data = app.as_dict()
        app_data = assoc(app_data, 'configurationkeys', list(map(lambda _: _.as_dict(), configurationkeys)))
        app_data = assoc(app_data, 'rangeconstraints', list(map(lambda _: _.as_dict(), ranges)))

        return app_data
