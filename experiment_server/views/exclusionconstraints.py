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
    def get_exclusionconstraint(self, app_id, conf_id, exconst_id):
        try:
            return ExclusionConstraint.query()\
                .join(ConfigurationKey, or_\
                    (ExclusionConstraint.first_configurationkey_id == ConfigurationKey.id,\
                    ExclusionConstraint.second_configurationkey_id == ConfigurationKey.id))\
                .join(Application)\
                .filter(ExclusionConstraint.id == exconst_id,\
                    ConfigurationKey.id == conf_id, Application.id == app_id)\
                .one()
        except Exception as e:
            print(e)
            return None


    """
        Route listeners
    """
    @view_config(route_name='exconstraints_for_configurationkey', request_method="GET")
    def exclusionconstraints_GET(self):
        """ List all exclusionconstraints with GET method """
        app_id = self.request.swagger_data['appid']
        conf_id = self.request.swagger_data['ckid']
        config = ConfigurationKey.query().join(Application)\
            .filter(ConfigurationKey.id == conf_id, Application.id == app_id)\
            .one_or_none()

        if config == None:
            print_log(datetime.datetime.now(), 'GET',
                '/applications/%s/configurationkeys/%s/exclusionconstraints'\
                    % (app_id, conf_id),
                'Get exclusionconstraints of one configurationkey', 'Failed')
            return self.createResponse(None, 400)

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
        """ Find and return one configurationkey by id with GET method """
        app_id = self.request.swagger_data['appid']
        conf_id = self.request.swagger_data['ckid']
        exconst_id = self.request.swagger_data['ecid']
        exconstraint = self.get_exclusionconstraint(app_id, conf_id, exconst_id)
        if exconstraint is None:
            print_log(datetime.datetime.now(), 'GET', '/exclusionconstraints/'
                      + str(exconst_id), 'Get one exclusionconstraint', 'Failed')
            return self.createResponse(None, 400)
        return exconstraint.as_dict()

    @view_config(route_name='exclusionconstraint', request_method="DELETE")
    def exclusionconstraints_DELETE_one(self):
        """ Find and delete one exclusionconstraint by id with DELETE method """
        app_id = self.request.swagger_data['appid']
        conf_id = self.request.swagger_data['ckid']
        exconst_id = self.request.swagger_data['ecid']
        exconstraint = self.get_exclusionconstraint(app_id, conf_id, exconst_id)

        logmessage_address = '/applications/%s/configurationkeys/%s/exclusionconstraints/%s'\
            % (app_id, conf_id, exconst_id)

        if not exconstraint:
            print_log(datetime.datetime.now(), 'DELETE', logmessage_address,
                'Delete exclusionconstraint', 'Failed')
            return self.createResponse(None, 400)
        ExclusionConstraint.destroy(exconstraint)
        print_log(datetime.datetime.now(), 'DELETE',
            logmessage_address, 'Delete exclusionconstraint', 'Succeeded')
        return {}

    @view_config(route_name='exconstraints_for_configurationkey', request_method="POST")
    def exclusionconstraints_for_confkey_POST(self):
        app_id = self.request.swagger_data['appid']
        first_config_id = self.request.swagger_data['ckid']
        exconstraint = self.request.swagger_data['exclusionconstraint']

        try:
            if first_config_id is None or exconstraint is None or app_id is None:
                raise Exception('Missing parameters')
            elif not ConfigurationKey.get(first_config_id).application_id == app_id:
                raise Exception('Application with id %s does not have ConfigurationKey with id %s'\
                    % (app_id, first_config_id))
            elif not ConfigurationKey.get(exconstraint.second_configurationkey_id).application_id == app_id:
                raise Exception('Application with id %s does not have ConfigurationKey with id %s'\
                    % (app_id, exconstraint.second_configurationkey_id))
        except Exception as e:
            print_log(datetime.datetime.now(), 'POST',
                '/application/%s/configurationkeys/%s/exclusionconstraints'\
                    % (app_id, first_config_id),
                'Create new exclusionconstraint for configurationkey', 'Failed')
            print_log(e)
            return self.createResponse({}, 400)

        new_exconstraint = ExclusionConstraint(
            first_configurationkey_id=first_config_id,
            first_operator_id=exconstraint.first_operator_id,
            first_value_a=exconstraint.first_value_a,
            first_value_b=exconstraint.first_value_b,

            second_configurationkey_id=exconstraint.second_configurationkey_id,
            second_operator_id=exconstraint.second_operator_id,
            second_value_a=exconstraint.second_value_a,
            second_value_b=exconstraint.second_value_b
        )
        ExclusionConstraint.save(new_exconstraint)
        return new_exconstraint.as_dict()
