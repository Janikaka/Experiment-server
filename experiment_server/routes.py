"This module contains all route-related functions"


def includeme(config):
    """Routes for every HTTP-endpoints"""
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('index', '/')

    config.add_route('applications', '/applications')
    config.add_route('application', '/applications/{id}')
    config.add_route('app_data', '/applications/{id}/data')

    config.add_route('configurationkeys_for_app', '/applications/{id}/configurationkeys')
    config.add_route('configurationkey', '/applications/{appId}/configurationkeys/{ckId}')

    config.add_route('rangeconstraints', '/applications/{appId}/configurationkeys/{ckId}/rangeconstraints')
    config.add_route('rangeconstraint', '/rangeconstraints/{id}')

    config.add_route('exconstraints_for_configurationkey', '/configurationkeys/{id}/exclusionconstraints')
    config.add_route('exclusionconstraints_for_app', '/applications/{id}/exclusionconstraints')
    config.add_route('exclusionconstraint', '/exclusionconstraints/{id}')

    config.add_route('clients', '/applications/{appId}/clients')
    config.add_route('client', '/applications/{appId}/clients/{clientId}')
    config.add_route('experiments_for_client', '/applications/{appId}/clients/{clientId}/experiments')
    config.add_route('configurations_for_client', '/applications/{appId}clients/{clientId}/configurations')

    config.add_route('operators', '/operators')

    config.add_route('experiments', '/experiments')
    config.add_route('experiment_metadata', '/experiments/{id}/metadata')
    config.add_route('experiment', '/experiments/{id}')
    config.add_route('experimentgroup', '/experiments/{expid}/experimentgroups/{expgroupid}')
    config.add_route('clients_for_experiment', '/experiments/{id}/clients')
    config.add_route('client_for_experiment', '/experiments/{expid}/clients/{clientid}')
    config.add_route('experiment_data', '/experiments/{id}/data')
    config.add_route('events', '/events')
