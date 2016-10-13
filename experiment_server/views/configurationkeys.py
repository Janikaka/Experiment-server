from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from ..models import DatabaseInterface
import datetime
from experiment_server.utils.log import print_log
from .webutils import WebUtils
from experiment_server.models.configurationkeys import ConfigurationKey
from experiment_server.models.applications import Application
from experiment_server.models.exclusionconstraints import ExclusionConstraint

@view_defaults(renderer='json')
class ConfigurationKeys(WebUtils):
    def __init__(self, request):
        self.request = request
        self.DB = DatabaseInterface(self.request.dbsession)


    """
        CORS-options
    """
    @view_config(route_name='configurationkeys', request_method="OPTIONS")
    def all_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS, DELETE, PUT')
        return res

    @view_config(route_name='configurationkey', request_method="OPTIONS")
    def all_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS, DELETE, PUT')
        return res

    @view_config(route_name='configurationkeys_for_app', request_method="OPTIONS")
    def all_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS, DELETE, PUT')
        return res

    @view_config(route_name='configurationkeys', request_method="GET")
    def configurationkeys_GET(self):
        """ List all configurationkeys with GET method """
        return list(map(lambda _: _.as_dict(), ConfigurationKey.all()))

    @view_config(route_name='configurationkey', request_method="GET")
    def configurationkeys_GET_one(self):
        """ Find and return one configurationkey by id with GET method """
        confkey_id = self.request.swagger_data['id']
        confkey = ConfigurationKey.get(confkey_id)
        if confkey is None:
            print_log(datetime.datetime.now(), 'GET', '/configurationkeys/'
                      + str(confkey_id), 'Get one configurationkey', None)
            return self.createResponse(None, 400)
        return confkey.as_dict()

    @view_config(route_name='configurationkey', request_method="PUT")
    def configurationkeys_PUT_one(self):
        """ Updates only the name of configurationkey"""
        configkey_req = self.request.swagger_data['configurationkey']
        ConfigurationKey.update(configkey_req.id, "name", configkey_req.name)
        updated = ConfigurationKey.get(configkey_req.id)
        return updated.as_dict()

    @view_config(route_name='configurationkey', request_method="DELETE")
    def configurationkeys_DELETE_one(self):
        """ Find and delete one configurationkey by id with destroy method """
        confkey_id = self.request.swagger_data['id']
        confkey = ConfigurationKey.get(confkey_id)
        if not confkey:
            print_log(datetime.datetime.now(), 'DELETE', '/configurationkeys/'
                      + str(confkey_id), 'Delete configurationkey', 'Failed')
            return self.createResponse(None, 400)
        ConfigurationKey.destroy(confkey)
        print_log(datetime.datetime.now(), 'DELETE', '/configurationkeys/'
                  + str(confkey_id), 'Delete configurationkey', 'Succeeded')
        return {}


    @view_config(route_name='rangeconstraints_for_configurationkey', request_method="GET")
    def rangeconstraints_for_confkey_GET(self):
        """ List all rangeconstraints of specific conf.key """
        confkey_id = self.request.swagger_data['id']
        confkey = ConfigurationKey.get(confkey_id)
        if confkey is None:
            print_log(datetime.datetime.now(), 'GET', '/configurationkeys/' + str(confkey_id) + '/rangeconstraints',
                      'Get rangeconstraints of one configurationkey', 'Failed')
            return self.createResponse(None, 400)
        return list(map(lambda _: _.as_dict(), confkey.rangeconstraints))

    @view_config(route_name='exconstraints_for_configurationkey', request_method="GET")
    def exclusionconstraints_for_confkey_GET(self):
        """ List all exclusionconstraints of specific con.key """
        confkey_id = self.request.swagger_data['id']
        confkey = ConfigurationKey.get(confkey_id)

        if confkey is None:
            print_log(datetime.datetime.now(), 'GET', '/configurationkeys/' + str(confkey_id) + '/exclusionconstraints',
                      'Get rangeconstraints of one configurationkey', 'Failed')
            return self.createResponse(None, 400)

        exclusionconstraints = ExclusionConstraint.all()
        result = list(map(lambda x: x.as_dict()
        if (x.first_configurationkey_id == confkey_id or x.second_configurationkey_id == confkey_id)
        else None, exclusionconstraints))
        return result

    @view_config(route_name='configurationkeys_for_app', request_method="POST")
    def configurationkeys_POST(self):
        """ Create new configurationkey to application.
            request.matchdict['id'] takes the id and DB.get_application_by_id(id) returns the application by id.
        """
        app_id = self.request.swagger_data['id']
        application = Application.get(app_id)
        if application is None:
            print_log(datetime.datetime.now(), 'POST', '/applications/' + str(app_id) + '/configurationkeys',
                      'Create new configurationkey for application', 'Failed')
            return self.createResponse({}, 400)
        new_confkey = self.request.swagger_data['configurationkey']
        name = new_confkey.name
        type = new_confkey.type
        configurationkey = ConfigurationKey(
            application=application,
            name=name,
            type=type
        )
        ConfigurationKey.save(configurationkey)
        print_log(datetime.datetime.now(), 'POST', '/applications/' + str(app_id) + '/configurationkeys',
                  'Create new configurationkey', 'Succeeded')
        return configurationkey.as_dict()

    @view_config(route_name='configurationkeys_for_app', request_method="DELETE")
    def configurationkeys_for_application_DELETE(self):
        """ Delete all configurationkeys for one specific application """
        id = self.request.swagger_data['id']
        app = Application.get(id)
        if not app:
            print_log(datetime.datetime.now(), 'DELETE', '/applications/' + str(id) + '/configurationkeys',
                      'Delete configurationkeys of application', 'Failed')
            return self.createResponse(None, 400)
        is_empty_list = list(map(lambda _: ConfigurationKey.destroy(_), app.configurationkeys))
        for i in is_empty_list:
            if i != None:
                print_log(datetime.datetime.now(), 'DELETE', '/applications/' + str(id) + '/configurationkeys',
                          'Delete configurationkeys of application', 'Failed')
                return self.createResponse(None, 400)
        print_log(datetime.datetime.now(), 'DELETE', '/applications/' + str(id) + '/configurationkeys',
                  'Delete configurationkeys of application', 'Succeeded')
        return {}
