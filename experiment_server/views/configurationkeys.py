import datetime

from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from experiment_server.models.applications import Application
from experiment_server.models.configurationkeys import ConfigurationKey
from experiment_server.utils.log import print_log
from experiment_server.utils.configuration_tools import get_valid_types
from .webutils import WebUtils

###
# Helper-functions and validations
###


def get_conf_key_by_appid_and_ckid(app_id, confkey_id):
    try:
        return ConfigurationKey.query()\
            .filter(ConfigurationKey.id == confkey_id)\
            .join(Application)\
            .filter(Application.id == app_id)\
            .one()
    except Exception as e:
        print_log(e)
        return None


def is_valid_name(ck):
    return ck.name is not None and len(ck.name) > 0


def is_valid_type(ck):
    return ck.type is not None and len(ck.type) > 0 and ck.type in get_valid_types()

###
# Controller-class and -functions
###


@view_defaults(renderer='json')
class ConfigurationKeys(WebUtils):
    def __init__(self, request):
        self.request = request

    """
        Helper-functions which are exported with ConfigurationKeys-class
    """

    def valid_types(self):
        return get_valid_types()

    def is_valid_configurationkey(self, ck):
        if not (is_valid_name(ck) and is_valid_type(ck)):
            return False
        return True

    """
        CORS-options
    """
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

    @view_config(route_name='configurationkeys_for_app', request_method="GET")
    def configurationkeys_GET(self):
        """ List all configurationkeys with GET method """
        app_id = self.request.swagger_data['id']
        if Application.get(app_id) is None:
            print_log(datetime.datetime.now(), 'GET', '/applications/%s/configurationkeys'\
                % app_id, 'Get configurationkeys', 'Failed')
            return self.createResponse(None, 400)
        app_conf_keys = ConfigurationKey.query().join(Application).filter(Application.id == app_id)
        return list(map(lambda _: _.as_dict(), app_conf_keys))

    @view_config(route_name='configurationkey', request_method="GET")
    def configurationkeys_GET_one(self):
        """ Find and return one configurationkey by id with GET method """
        app_id = self.request.swagger_data['appid']
        confkey_id = self.request.swagger_data['ckid']
        confkey = get_conf_key_by_appid_and_ckid(app_id, confkey_id)
        if confkey is None:
            print_log(datetime.datetime.now(), 'GET',\
                '/applications/%s/configurationkeys/' % app_id
                + str(confkey_id), 'Get one configurationkey', 'Failed')
            return self.createResponse(None, 400)
        return confkey.as_dict()

    @view_config(route_name='configurationkey', request_method="PUT")
    def configurationkeys_PUT_one(self):
        """ Updates only the name of configurationkey"""
        app_id = self.request.swagger_data['appid']
        confkey_id = self.request.swagger_data['ckid']
        configkey_req = self.request.swagger_data['configurationkey']
        if self.is_valid_configurationkey(configkey_req):
            ConfigurationKey.update(configkey_req.id, "name", configkey_req.name)
            updated = ConfigurationKey.get(configkey_req.id)
            return updated.as_dict()

        print_log(datetime.datetime.now(), 'PUT', 'applications/%s/configurationkeys/%s' % (app_id, confkey_id),
                  'Update ConfigurationKey', 'Failed: Invalid Configurationkey')
        return self.createResponse('Bad Request: invalid ConfigurationKey', 400)

    @view_config(route_name='configurationkey', request_method="DELETE")
    def configurationkeys_DELETE_one(self):
        """ Find and delete one configurationkey by id with delete method """
        confkey_id = self.request.swagger_data['ckid']
        app_id = self.request.swagger_data['appid']
        confkey = get_conf_key_by_appid_and_ckid(app_id, confkey_id)
        if not confkey:
            print_log(datetime.datetime.now(), 'DELETE', '/applications/%s/' % app_id +
                '/configurationkeys/%s/' % confkey_id,
                 'Delete configurationkey', 'Failed')
            return self.createResponse(None, 400)
        ConfigurationKey.destroy(confkey)
        print_log(datetime.datetime.now(), 'DELETE', '/applications/%s' % app_id +
            '/configurationkeys/%s' % confkey_id, 'Delete configurationkey', 'Succeeded')
        return {}


    @view_config(route_name='configurationkeys_for_app', request_method="POST")
    def configurationkeys_POST(self):
        """
            Create new configurationkey to application.
            request.swagger_data['id'] takes the id and Application.get(app_id) returns the application by id.
        """
        app_id = self.request.swagger_data['id']
        application = Application.get(app_id)
        if application is None:
            print_log(datetime.datetime.now(), 'POST', '/applications/' + str(app_id) + '/configurationkeys',
                      'Create new configurationkey for application', 'Failed: No Application with id %s' % app_id)
            return self.createResponse({}, 400)
        new_confkey = self.request.swagger_data['configurationkey']
        name = new_confkey.name
        type = new_confkey.type.lower()
        configurationkey = ConfigurationKey(
            application=application,
            name=name,
            type=type
        )

        if self.is_valid_configurationkey(configurationkey):
            ConfigurationKey.save(configurationkey)
            print_log(datetime.datetime.now(), 'POST', '/applications/' + str(app_id) + '/configurationkeys',
                      'Create new configurationkey', 'Succeeded')
            return configurationkey.as_dict()

        print_log(datetime.datetime.now(), 'POST', '/applications/' + str(app_id) + '/configurationkeys',
                  'Create new configurationkey for application', 'Failed: Invalid ConfigurationKey')
        return self.createResponse({}, 400)

    @view_config(route_name='configurationkeys_for_app', request_method="DELETE")
    def configurationkeys_for_application_DELETE(self):
        """ Delete all configurationkeys of one specific application """
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
