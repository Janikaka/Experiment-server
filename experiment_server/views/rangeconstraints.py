from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from ..models import DatabaseInterface
import datetime
from experiment_server.utils.log import print_log
from .webutils import WebUtils
from experiment_server.models.rangeconstraints import RangeConstraint
from experiment_server.models.configurationkeys import ConfigurationKey
from experiment_server.models.operators import Operator
from experiment_server.models.dictionary_creator import DictionaryCreator
import sqlalchemy.orm.exc


@view_defaults(renderer='json')
class Applications(WebUtils):
    def __init__(self, request):
        self.request = request
        self.DB = DatabaseInterface(self.request.dbsession)

    @view_config(route_name='rangeconstraints', request_method="GET")
    def rangeconstraints_GET(self):
        """ List all rangeconstraints with GET method """
        return list(map(lambda _: _.as_dict(), RangeConstraint.all()))

    @view_config(route_name='rangeconstraints_for_configurationkey', request_method="POST")
    def rangecontraints_POST(self):
        """ Create new rangeconstraint for specific configurationkey """
        # TODO Decide how to receive operator.id
        data = self.request.json_body
        ck_id = int(self.request.matchdict['id'])
        conf_key = ConfigurationKey.get(ck_id)
        op_id = self.request.headers.get('operator') # Change this. Now it takes id from header.
        operator = Operator.get(op_id)
        value = data['value']
        if (conf_key == None):
            return "There's no id:" +str(ck_id)+ " in configurationkeys table."
        elif (operator == None):
            return "There's no id:" +str(op_id)+ " in operators table."
        else:
            rc = self.DB.create_rangeconstraint(
                {
                    'configurationkey': conf_key,
                    'operator': operator,
                    'value': value
                })

            result = {'data': DictionaryCreator.as_dict(rc)}
            return self.createResponse(result, 200)

    @view_config(route_name='rangeconstraint', request_method="DELETE")
    def rangecontraints_DELETE_one(self):
        """ Find and delete one rangeconstraint by id with destroy method """
        rc_id = self.request.swagger_data['id']
        rangeconstraint = RangeConstraint.get(rc_id)
        if not rangeconstraint:
            print_log(datetime.datetime.now(), 'DELETE', '/rangeconstraint/' + str(rc_id),
                      'Delete rangeconstraint', 'Failed')
            return self.createResponse(None, 400)
        RangeConstraint.destroy(rangeconstraint)
        print_log(datetime.datetime.now(), 'DELETE', '/rangeconstranit/' + str(rc_id),
                  'Delete rangeconstraint', 'Succeeded')
        return self.createResponse(None, 200)

    @view_config(route_name='rangeconstraints_for_configurationkey', request_method="DELETE")
    def rangeconstraints_for_configuratinkey_DELETE(self):
        """ Delete all rangeconstraints for one specific configurationkey"""
        id = self.request.swagger_data['id']
        con_key = ConfigurationKey.get(id)
        if not con_key:
            print_log(datetime.datetime.now(), 'DELETE', '/configurationkeys/' + str(id) +'/rangeconstraints',
                      'Delete rangeconstraints of configurationkey', 'Failed')
            return self.createResponse(None, 400)
        is_empty_list = list(map(lambda _: RangeConstraint.destroy(_), con_key.rangeconstraints))
        for i in is_empty_list:
            if i != None:
                return self.createResponse(None, 400)
        return self.createResponse(None, 200)
