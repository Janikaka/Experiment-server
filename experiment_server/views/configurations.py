from ..models import (Application, Configuration, ConfigurationKey, Experiment, ExperimentGroup)
from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from experiment_server.utils.log import print_log
from .webutils import WebUtils
import datetime


def get_configurationkey(app_id, configuration):
    """
    Retrieves ConfigurationKey by Application's id and Configuration's key.
    Combination of app_id and ConfigurationKey should be unique.
    :param app_id: Application's id
    :param configuration: Configuration to be validated
    :return: ConfigurationKey, if such exists.
    """
    return ConfigurationKey.query().join(Application) \
        .filter(Application.id == app_id, ConfigurationKey.name == configuration.key) \
        .one_or_none()


def is_valid_value(app_id, configuration):
    """
    Valiates Configuration's value.
    :param app_id: Application's id
    :param configuration: Configuration to be validated
    :return: Is configuration's value valid
    """
    from experiment_server.utils.configuration_tools import (is_valid_type_value, is_in_range, is_valid_exclusion)

    confkey = get_configurationkey(app_id, configuration)
    value = configuration.value

    if confkey is not None:
        return is_valid_type_value(confkey.type, configuration.value) \
               and is_in_range(confkey, value) and is_valid_exclusion(confkey, configuration)

    return False


def exists_configurationkey(app_id, configuration):
    """
    Checks if given ConfigurationKey exists. Combination of app_id and ConfigurationKey should be unique
    :param app_id: Application's id
    :param configuration: Configuration to be validated
    :return: Does given ConfigurationKey exist
    """
    confkey = get_configurationkey(app_id, configuration)

    return confkey is not None


def is_valid_connections(app_id, exp_id, expgroup_id):
    """
    Checks if ExperimentGroup exists under given Experiment and Application
    :param app_id: Application where Experiment belongs
    :param exp_id: Experiment where ExperimentGroup belongs
    :param expgroup_id: ExperimentGroup
    :return: Does such ExperimentGroup exist
    """
    expgroup = ExperimentGroup().query().join(Experiment, Application)\
        .filter(ExperimentGroup.id == expgroup_id, Experiment.id == exp_id, Application.id == app_id).one_or_none()

    return expgroup is not None


@view_defaults(renderer='json')
class Configurations(WebUtils):
    def __init__(self, request):
        self.request = request

    def is_valid_configuration(self, app_id, exp_id, expgroup_id, configuration):
        """
        Validates Configuration. Only this function should be called when validating Configuration.
        :param app_id: Application's id in which Experiment should belong to
        :param exp_id: Experiment's id in which ExperimentGroup should belong to
        :param expgroup_id: ExperimentGroup's id in which Configuration is goint to be created to
        :param configuration: Configuration to be validated
        :return: Is configuration valid
        """
        return is_valid_connections(app_id, exp_id, expgroup_id) and exists_configurationkey(app_id, configuration) \
               and is_valid_value(app_id, configuration)

    @view_config(route_name='experimentgroup_configuration', request_method="OPTIONS")
    def all_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'OPTIONS, DELETE')
        return res\

    @view_config(route_name='experimentgroup_configurations', request_method="OPTIONS")
    def all_OPTIONS(self):
        res = Response()
        res.headers.add('Access-Control-Allow-Origin', '*')
        res.headers.add('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        return res

    @view_config(route_name='experimentgroup_configurations', request_method="GET")
    def configurations_GET(self):
        """
        Get all Configurations for a ExperimentGroup. Requires Application's id, Experiment's id and
        ExperimentGroup's id.
        :return: Listed configurations. If id's do not match or there is no configurations for this ExperimentGroup,
        empty list will be returned.
        """
        app_id = self.request.swagger_data['appid']
        exp_id = self.request.swagger_data['expid']
        expgroup_id = self.request.swagger_data['expgroupid']

        configurations = Configuration.query().join(ExperimentGroup, Experiment, Application)\
            .filter(ExperimentGroup.id == expgroup_id, Experiment.id == exp_id, Application.id == app_id).all()

        return list(map(lambda _: _.as_dict(), configurations))

    @view_config(route_name='experimentgroup_configurations', request_method="POST")
    def configurations_POST(self):
        """
        Create new Configuration to ExperimentGroup. Requires Application's id, Experiment's id, ExperimentGroup's id
        and Configuration to be created. This will fail if Configuration, or given ids are not valid.
        :return: If successfully created, returns created Configuration. If it fails, returns response with HTTP code 400
        """
        app_id = self.request.swagger_data['appid']
        exp_id = self.request.swagger_data['expid']
        expgroup_id = self.request.swagger_data['expgroupid']
        req_config = self.request.swagger_data['configuration']

        req_config.experimentgroup_id = expgroup_id

        if self.is_valid_configuration(app_id, exp_id, expgroup_id, req_config):
            Configuration.save(req_config)
            print_log(datetime.datetime.now(), 'POST', '/applications/%s/experiments/%s/experimentgroups/%s',
                      'Create Configuration to ExperimentGroup', 'Success')
            return req_config.as_dict()

        print_log(datetime.datetime.now(), 'POST', '/applications/%s/experiments/%s/experimentgroups/%s',
                  'Create Configuration to ExperimentGroup', 'Failed: Invalid Configuration')
        return self.createResponse(None, 400)