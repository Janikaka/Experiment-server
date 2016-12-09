from sqlalchemy.sql import exists
from sqlalchemy import or_
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
import datetime
from experiment_server.utils.log import print_log
from .webutils import WebUtils
from experiment_server.models.exclusionconstraints import ExclusionConstraint
from experiment_server.models.configurationkeys import ConfigurationKey
from experiment_server.models.applications import Application

def has_all_ids(exconstraint, app_id):
    return not (exconstraint.first_configurationkey_id is None) or \
        (exconstraint.second_configurationkey_id is None) or \
        (exconstraint is None or app_id is None)

def is_configurationkeys_from_same_app(exconstraint, app_id):
    if not ConfigurationKey.get(exconstraint.first_configurationkey_id).application_id == app_id:
        return False

    elif not ConfigurationKey.get(exconstraint.second_configurationkey_id).application_id == app_id:
        return False

    return True

def is_values_valid_to_configurationkeys(exconstraint):
    from experiment_server.utils.configuration_tools import is_valid_type_operator
    from experiment_server.utils.configuration_tools import is_valid_type_values

    first_ckey_type = ConfigurationKey.get(exconstraint.first_configurationkey_id).type
    second_ckey_type = ConfigurationKey.get(exconstraint.second_configurationkey_id).type

    return is_valid_type_operator(first_ckey_type,
                                  exconstraint.first_operator) \
           and is_valid_type_operator(second_ckey_type,
                                      exconstraint.second_operator) \
           and is_valid_type_values(first_ckey_type,
                                    exconstraint.first_operator,
                                    [exconstraint.first_value_a, exconstraint.first_value_a]) \
           and is_valid_type_values(second_ckey_type,
                                    exconstraint.second_operator,
                                    [exconstraint.second_value_a, exconstraint.second_value_b])

@view_defaults(renderer='json')
class ExclusionConstraints(WebUtils):
    def __init__(self, request):
        self.request = request

    """
        CORS-options
    """
    @view_config(route_name='exconstraints_for_configurationkey', request_method="OPTIONS")
    def all_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS, DELETE, PUT')
        return res

    @view_config(route_name='exclusionconstraint', request_method="OPTIONS")
    def all_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST,GET,OPTIONS, DELETE, PUT')
        return res

    """
        Helper functions
    """
    def get_exclusionconstraint(self, app_id, exconst_id):
        try:
            return ExclusionConstraint.query()\
                .join(ConfigurationKey, or_\
                    (ExclusionConstraint.first_configurationkey_id == ConfigurationKey.id,\
                    ExclusionConstraint.second_configurationkey_id == ConfigurationKey.id))\
                .join(Application)\
                .filter(Application.id == app_id, \
                    ExclusionConstraint.id == exconst_id)\
                .one_or_none()
        except Exception as e:
            print(e)
            return None

    def is_valid_exclusionconstraint(self, exconstraint, app_id):
        return has_all_ids(exconstraint, app_id) and is_configurationkeys_from_same_app(exconstraint, app_id) \
               and is_values_valid_to_configurationkeys(exconstraint)

    """
        Route listeners
    """
    @view_config(route_name='exconstraints_for_configurationkey', request_method="GET")
    def exclusionconstraints_GET(self):
        """ List all exclusionconstraints for Application with GET method """
        app_id = self.request.swagger_data['appid']

        exclusionconstraints = ExclusionConstraint.query()\
            .join(ConfigurationKey, \
                or_(ConfigurationKey.id == ExclusionConstraint.first_configurationkey_id, \
                    ConfigurationKey.id == ExclusionConstraint.second_operator_id))\
            .join(Application)\
            .filter(Application.id == app_id)\
            .all()

        return list(map(lambda _: _.as_dict(), exclusionconstraints))

    @view_config(route_name='exclusionconstraint', request_method="GET")
    def exclusionconstraints_GET_one(self):
        """ Find and return one ExclusionConstraint by id with GET method """
        app_id = self.request.swagger_data['appid']
        exconst_id = self.request.swagger_data['ecid']
        exconstraint = self.get_exclusionconstraint(app_id, exconst_id)
        if exconstraint is None:
            print_log(datetime.datetime.now(), 'GET', '/applications/%s/exclusionconstraints/'
                      + str(exconst_id) % app_id, 'Get one exclusionconstraint', 'Failed')
            return self.createResponse(None, 400)
        return exconstraint.as_dict()

    @view_config(route_name='exclusionconstraint', request_method="DELETE")
    def exclusionconstraints_DELETE_one(self):
        """ Find and delete one exclusionconstraint by id with DELETE method """
        app_id = self.request.swagger_data['appid']
        exconst_id = self.request.swagger_data['ecid']
        exconstraint = self.get_exclusionconstraint(app_id, exconst_id)

        logmessage_address = '/applications/%s/exclusionconstraints/%s'\
            % (app_id, exconst_id)

        if exconstraint is None:
            print_log(datetime.datetime.now(), 'DELETE', logmessage_address,
                'Delete exclusionconstraint', 'Failed')
            return self.createResponse(None, 400)

        ExclusionConstraint.destroy(exconstraint)
        print_log(datetime.datetime.now(), 'DELETE',
            logmessage_address, 'Delete exclusionconstraint', 'Succeeded')
        return {}

    @view_config(route_name='exconstraints_for_configurationkey', request_method="POST")
    def exclusionconstraints_POST(self):
        app_id = self.request.swagger_data['appid']
        exconstraint = self.request.swagger_data['exclusionconstraint']

        new_exconstraint = ExclusionConstraint(
            first_configurationkey_id=exconstraint['first_configurationkey_id'],
            first_operator_id=exconstraint['first_operator_id'],
            first_value_a=None if len(exconstraint['first_value']) == 0 else exconstraint['first_value'][0],
            first_value_b=None if len(exconstraint['first_value']) <= 1 else exconstraint['first_value'][1],

            second_configurationkey_id=exconstraint['second_configurationkey_id'],
            second_operator_id=exconstraint['second_operator_id'],
            second_value_a=None if len(exconstraint['second_value']) == 0 else exconstraint['second_value'][0],
            second_value_b=None if len(exconstraint['second_value']) <= 1 else exconstraint['second_value'][1]
        )

        if not self.is_valid_exclusionconstraint(new_exconstraint, app_id):
            print_log(datetime.datetime.now(), 'POST',
                      '/application/%s/exclusionconstraints' % (app_id),
                      'Create new exclusionconstraint for configurationkey', 'Failed: ExclusionConstraint is not valid: %s'
                      % (new_exconstraint.as_dict()))

            return self.createResponse({}, 400)

        ExclusionConstraint.save(new_exconstraint)

        return new_exconstraint.as_dict()
