from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from ..models import DatabaseInterface
from .webutils import WebUtils
from experiment_server.models.rangeconstraints import RangeConstraint
from experiment_server.models.configurationkeys import ConfigurationKey
from experiment_server.models.operators import Operator
from experiment_server.models.dictionary_creator import DictionaryCreator


@view_defaults(renderer='json')
class Applications(WebUtils):
    def __init__(self, request):
        self.request = request
        self.DB = DatabaseInterface(self.request.dbsession)

    @view_config(route_name='rangecontraints_for_configurationkey', request_method="POST")
    def rangecontraints_POST(self):
        """ Create new rangeconstraint for specific configurationkey """
        # TODO Decide hot to receive operator.id
        data = self.request.json_body
        ck_id = int(self.request.matchdict['id'])
        conf_key = ConfigurationKey.get(ck_id)
        op_id = self.request.headers.get('operator') # Change this. Now it takes id from header.
        operator = Operator.get(op_id)
        value = data['value']

        rc = self.DB.create_rangeconstraint(
            {
                'configurationkey': conf_key,
                'operator': operator,
                'value': value
            })

        result = {'data': DictionaryCreator.as_dict(rc)}
        return self.createResponse(result, 200)