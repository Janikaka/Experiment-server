from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from ..models import DatabaseInterface
import datetime
from experiment_server.utils.log import print_log
from .webutils import WebUtils
from experiment_server.models.configurationkeys import ConfigurationKey


@view_defaults(renderer='json')
class ConfigurationKeys(WebUtils):
    def __init__(self, request):
        self.request = request
        self.DB = DatabaseInterface(self.request.dbsession)

    @view_config(route_name='configurationkeys', request_method="GET")
    def configurationkeys_GET(self):
        """ List all configurationkeys with GET method """
        return list(map(lambda _: _.as_dict(), ConfigurationKey.all()))

    @view_config(route_name='configurationkeys_for_app', request_method="POST")
    def configurationkeys_POST(self):
        """ Create new configurationkey to application.
            request.matchdict['id'] takes the id and DB.get_application_by_id(id) returns the application by id.
        """
        data = self.request.json_body
        id = int(self.request.matchdict['id'])
        application = self.DB.get_application_by_id(id)
        name = data['name']
        type = data['type']

        configurationkey = self.DB.create_configurationkey(
            {
                'application': application,
                'name': name,
                'type': type,
            })
        result = {'data': configurationkey.as_dict()}
        print_log(name, 'POST', '/applications/{id}/configurationkeys', 'Create new configurationkey', result)
        return self.createResponse(result, 200)

