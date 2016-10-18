from pyramid.view import view_config, view_defaults
from pyramid.response import Response
import datetime
from experiment_server.utils.log import print_log
from .webutils import WebUtils
from experiment_server.models.rangeconstraints import RangeConstraint
from experiment_server.models.configurationkeys import ConfigurationKey


@view_defaults(renderer='json')
class RangeConstraints(WebUtils):
    def __init__(self, request):
        self.request = request

    """
        CORS-options
    """
    @view_config(route_name='rangeconstraints', request_method="OPTIONS")
    def all_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS, DELETE, PUT')
        return res

    @view_config(route_name='rangeconstraints_for_configurationkey', request_method="OPTIONS")
    def all_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS, DELETE, PUT')
        return res

    @view_config(route_name='rangeconstraint', request_method="OPTIONS")
    def all_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS, DELETE, PUT')
        return res

    @view_config(route_name='rangeconstraints', request_method="GET")
    def rangeconstraints_GET(self):
        """ List all rangeconstraints with GET method """
        return list(map(lambda _: _.as_dict(), RangeConstraint.all()))

    @view_config(route_name='rangeconstraint', request_method="DELETE")
    def rangecontraints_DELETE_one(self):
        """ Find and delete one rangeconstraint by id with DELETE method """
        rc_id = self.request.swagger_data['id']
        rangeconstraint = RangeConstraint.get(rc_id)
        if not rangeconstraint:
            print_log(datetime.datetime.now(), 'DELETE', '/rangeconstraint/' + str(rc_id),
                      'Delete rangeconstraint', 'Failed')
            return self.createResponse(None, 400)
        RangeConstraint.destroy(rangeconstraint)
        print_log(datetime.datetime.now(), 'DELETE', '/rangeconstranit/' + str(rc_id),
                  'Delete rangeconstraint', 'Succeeded')
        return {}

    @view_config(route_name='rangeconstraints_for_configurationkey', request_method="POST")
    def rangecontraints_POST(self):
        """ Create new rangeconstraint for specific configurationkey """
        req_rangec = self.request.swagger_data['rangeconstraint']
        configkey_id = self.request.swagger_data['id']

        rconstraint = RangeConstraint(
            configurationkey_id=configkey_id,
            operator_id=req_rangec.operator_id,
            value=req_rangec.value
        )

        try:
            RangeConstraint.save(rconstraint)
        except:
            return self.createResponse({}, 400)

        print_log(datetime.datetime.now(), 'POST', '/configurationkeys/' + '{id}' + '/rangeconstraints',
                  'Create new rangeconstraint for configurationkey', 'Succeeded')
        return rconstraint.as_dict()

    @view_config(route_name='rangeconstraints_for_configurationkey', request_method="DELETE")
    def rangeconstraints_for_configuratinkey_DELETE(self):
        """ Delete all rangeconstraints of one specific configurationkey"""
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
        print_log(datetime.datetime.now(), 'DELETE', '/configurationkeys/' + str(id) + '/rangeconstraints',
                  'Delete rangeconstraints of configurationkey', 'Succeeded')
        return {}
