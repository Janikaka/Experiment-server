from pyramid.view import view_config, view_defaults
from pyramid.response import Response
import datetime
from experiment_server.utils.log import print_log
from .webutils import WebUtils
from experiment_server.models.rangeconstraints import RangeConstraint
from experiment_server.models.configurationkeys import ConfigurationKey
from experiment_server.models.applications import Application

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
        """ List all rangeconstraints for ConfigurationKey with GET method """
        app_id = self.request.swagger_data['appId']
        confkey_id = self.request.swagger_data['ckId']
        rangeconstraints = RangeConstraint.query()\
            .join(ConfigurationKey)\
            .filter(ConfigurationKey.id == confkey_id)\
            .join(Application)\
            .filter(Application.id == app_id)
        return list(map(lambda _: _.as_dict(), rangeconstraints))

    @view_config(route_name='rangeconstraint', request_method="DELETE")
    def rangecontraints_DELETE_one(self):
        """ Find and delete one rangeconstraint by id with DELETE method """
        app_id = self.request.swagger_data['appId']
        confkey_id = self.request.swagger_data['ckId']
        rc_id = self.request.swagger_data['rcId']
        rangeconstraint = RangeConstraint.get(rc_id)

        try:
            # Checks if ConfigurationKey exists with given Application
            if not ConfigurationKey.get(confkey_id).application_id == app_id:
                raise Exception('Application with id %s does not have' % app_id +
                    ' ConfigurationKey with id %s' % confkey_id)
            # Checks if given RangeConstraint is owned by ConfigurationKey
            elif not rangeconstraint.configurationkey_id == confkey_id:
                raise Exception('ConfigurationKey with id %s does not' % confkey_id +
                    ' have RangeConstraint with id %s' % rc_id)

            RangeConstraint.destroy(rangeconstraint)
        except Exception as e:
            print(e)
            print_log(datetime.datetime.now(), 'DELETE', '/rangeconstraint/' + str(rc_id),
                      'Delete rangeconstraint', 'Failed')
            return self.createResponse(None, 400)

        print_log(datetime.datetime.now(), 'DELETE', '/rangeconstranit/' + str(rc_id),
                  'Delete rangeconstraint', 'Succeeded')
        return {}

    @view_config(route_name='rangeconstraints', request_method="POST")
    def rangecontraints_POST(self):
        """ Create new rangeconstraint for specific configurationkey """
        req_rangec = self.request.swagger_data['rangeconstraint']
        configkey_id = self.request.swagger_data['ckId']
        app_id = self.request.swagger_data['appId']

        rconstraint = RangeConstraint(
            configurationkey_id=configkey_id,
            operator_id=req_rangec.operator_id,
            value=req_rangec.value
        )

        try:
            # Checks if Configuration with such connection to Application exists
            if ConfigurationKey.get(configkey_id).application_id != app_id:
                raise Exception('Application with id %s does not have' % app_id +
                    ' ConfigurationKey with id %s' % configkey_id)
            RangeConstraint.save(rconstraint)
        except:
            print(e)
            print_log(datetime.datetime.now(), 'POST', '/applications/%s/' % app_id +
                'configurationkeys/%s/rangeconstraints' % confkey_id,
                'Create new rangeconstraint for configurationkey', 'Failed')
            return self.createResponse({}, 400)

        print_log(datetime.datetime.now(), 'POST', '/applications/%s' % app_id +
            '/configurationkeys/%s/rangeconstraints' % configkey_id,
            'Create new rangeconstraint for configurationkey', 'Succeeded')
        return rconstraint.as_dict()

    # To include all the database connection checks which
    # rangecontraints_DELETE_one contains, it is included in this function
    @view_config(route_name='rangeconstraints', request_method="DELETE")
    def rangeconstraints_for_configuratinkey_DELETE(self):
        """ Delete all rangeconstraints of one specific configurationkey"""
        configkey_id = self.request.swagger_data['ckId']
        app_id = self.request.swagger_data['appId']
        configurationkey = ConfigurationKey.get(configkey_id)
        errors = 0

        try:
            for rc in configurationkey.rangeconstraints:
                # Set rangeconstraint's id, so rangecontraints_DELETE_one can use it
                self.request.swagger_data['rcId'] = rc.id
                if not self.rangecontraints_DELETE_one() == {}:
                    errors += 1
        except Exception as e:
            print(e)
            errors += 1
        finally:
            if (errors > 0):
                print_log(datetime.datetime.now(), 'DELETE', '/application/%s' % app_id +
                    '/configurationkeys/' + str(configkey_id) +'/rangeconstraints',
                    'Delete rangeconstraints of configurationkey', 'Failed')
                return self.createResponse(None, 400)

        return {}
