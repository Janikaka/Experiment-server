from pyramid.view import view_config, view_defaults
from pyramid.response import Response
import datetime
from experiment_server.utils.log import print_log
from .webutils import WebUtils
from experiment_server.models.configurationkeys import ConfigurationKey
from experiment_server.models.applications import Application

"""
Helper functions
"""
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

@view_defaults(renderer='json')
class ConfigurationKeys(WebUtils):
    def __init__(self, request):
        self.request = request


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
        confkey_id = self.request.swagger_data['ckid']
        app_id = self.request.swagger_data['appid']
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
        configkey_req = self.request.swagger_data['configurationkey']
        ConfigurationKey.update(configkey_req.id, "name", configkey_req.name)
        updated = ConfigurationKey.get(configkey_req.id)
        return updated.as_dict()

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
        """ Create new configurationkey to application.
            request.swagger_data['id'] takes the id and Application.get(app_id) returns the application by id.
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
