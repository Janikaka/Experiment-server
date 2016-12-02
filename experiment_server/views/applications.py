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

    def get_app_exclusionconstraints(self, app_id):
        from experiment_server.models.exclusionconstraints import ExclusionConstraint
        from experiment_server.models.configurationkeys import ConfigurationKey
        from sqlalchemy import or_

        exclusions = ExclusionConstraint.query()\
            .join(ConfigurationKey, \
                or_(ExclusionConstraint.first_configurationkey_id == ConfigurationKey.id, \
                    ExclusionConstraint.second_configurationkey_id == ConfigurationKey.id))\
            .join(Application).filter(Application.id == app_id)

        return exclusions

    """
        Route listeners
    """

    @view_config(route_name='application', request_method="GET")
    def applications_GET_one(self):
        """ Find and return one application by id with GET method """
        app_id = self.request.swagger_data['appid']
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
        app_id = self.request.swagger_data['appid']
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
            Returns application with configurationkeys, rangeconstraints and exclusionconstraints
        """
        app_id = self.request.swagger_data['appid']
        app = Application.get(app_id)
        if app is None:
            print_log(datetime.datetime.now(), 'GET', '/applications/' + str(id) + '/rangeconstraints',
                      'Get all things of one application', None)
            return self.createResponse(None, 400)
        if app.apikey is None:
            app = self.set_app_apikey(app, app_id)
        configurationkeys = app.configurationkeys
        ranges = list(concat(list(map(lambda _: _.rangeconstraints, configurationkeys))))
        exclusions = self.get_app_exclusionconstraints(app_id)

        app_data = app.as_dict()
        app_data = assoc(app_data, 'configurationkeys', list(map(lambda _: _.as_dict(), configurationkeys)))
        app_data = assoc(app_data, 'rangeconstraints', list(map(lambda _: _.as_dict(), ranges)))
        app_data = assoc(app_data, 'exclusionconstraints', list(map(lambda _: _.as_dict(), exclusions)))

        return app_data

    @view_config(route_name='application', request_method="PUT")
    def applications_PUT(self):
        req_app = self.request.swagger_data['application']
        req_app_id = self.request.swagger_data['appid']
        updated = Application.get(req_app_id)

        if req_app_id != req_app['id'] or updated is None:
            print_log(datetime.datetime.now(), 'PUT', '/applications/',
                      'Update Application', 'Failed: no such Application with id %s or ids didn\'t match' % req_app_id)
            return self.createResponse(None, 400)

        updated.name = req_app['name']
        Application.save(updated)

        return updated.as_dict()
