from pyramid.view import view_config, view_defaults
from pyramid.response import Response
import datetime
from experiment_server.utils.log import print_log
from .webutils import WebUtils
from experiment_server.models.exclusionconstraints import ExclusionConstraint


@view_defaults(renderer='json')
class ExclusionConstraints(WebUtils):
    def __init__(self, request):
        self.request = request

    """
        CORS-options
    """
    @view_config(route_name='exclusionconstraints', request_method="OPTIONS")
    def all_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS, DELETE, PUT')
        return res

    @view_config(route_name='exclusionconstraints_for_app', request_method="OPTIONS")
    def all_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS, DELETE, PUT')
        return res

    @view_config(route_name='exclusionconstraints', request_method="GET")
    def exclusionconstraints_GET(self):
        """ List all exclusionconstraints with GET method """
        return list(map(lambda _: _.as_dict(), ExclusionConstraint.all()))

    @view_config(route_name='exclusionconstraint', request_method="GET")
    def exclusionconstraints_GET_one(self):
        """ Find and return one configurationkey by id with GET method """
        exconst_id = self.request.swagger_data['id']
        exconstraint = ExclusionConstraint.get(exconst_id)
        if exconstraint is None:
            print_log(datetime.datetime.now(), 'GET', '/exclusionconstraints/'
                      + str(exconst_id), 'Get one exclusionconstraint', 'Failed')
            return self.createResponse(None, 400)
        return exconstraint.as_dict()

    @view_config(route_name='exclusionconstraint', request_method="DELETE")
    def exclusionconstraints_DELETE_one(self):
        """ Find and delete one exclusionconstraint by id with DELETE method """
        exconst_id = self.request.swagger_data['id']
        exconstraint = ExclusionConstraint.get(exconst_id)
        if not exconstraint:
            print_log(datetime.datetime.now(), 'DELETE', '/exclusionconstraints/'
                      + str(exconst_id), 'Delete exclusionconstraint', 'Failed')
            return self.createResponse(None, 400)
        ExclusionConstraint.destroy(exconstraint)
        print_log(datetime.datetime.now(), 'DELETE', '/exclusionconstraints/'
                  + str(exconst_id), 'Delete exclusionconstraint', 'Succeeded')
        return {}

    @view_config(route_name='exclusionconstraints_for_app', request_method="POST")
    def create_exclusionconstraint_for_app(self):
        app_id = self.request.swagger_data['id']
        exconstraint = self.request.swagger_data['exclusionconstraint']

        if app_id is None or exconstraint is None:
            print_log(datetime.datetime.now(), 'POST', '/applications/' + str(app_id) + '/exclusionconstraints',
                      'Create new exclusionconstraint for application', 'Failed')
            return self.createResponse({}, 400)

        new_exconstraint = ExclusionConstraint(
            first_configurationkey_id = exconstraint.first_configurationkey_id,
            first_operator_id = exconstraint.first_operator_id,
            first_value_a = exconstraint.first_value_a,
            first_value_b = exconstraint.first_value_b,

            second_configurationkey_id = exconstraint.second_configurationkey_id,
            second_operator_id = exconstraint.second_operator_id,
            second_value_a = exconstraint.second_value_a,
            second_value_b = exconstraint.second_value_b
        )
        ExclusionConstraint.save(new_exconstraint)
        return new_exconstraint.as_dict()