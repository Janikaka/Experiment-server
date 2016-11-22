"This module contains all route-related functions"


def includeme(config):
    """Routes for every HTTP-endpoints"""
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('index', '/')

    config.add_route('events', '/events')
    config.add_route('operators', '/operators')

    config.add_route('applications', '/applications')
    config.add_route('application', '/applications/{id}')
    config.add_route('app_data', '/applications/{id}/data')

    config.add_route('configurationkey', '/applications/{appid}/configurationkeys/{ckid}')
    config.add_route('configurationkeys_for_app', '/applications/{id}/configurationkeys')

    config.add_route('rangeconstraints', '/applications/{appid}/configurationkeys/{ckid}/rangeconstraints')
    config.add_route('rangeconstraint', '/applications/{appid}/configurationkeys/{ckid}/rangeconstraints/{rcid}')

    config.add_route('exconstraints_for_configurationkey', '/applications/{appid}/configurationkeys/{ckid}/exclusionconstraints')
    config.add_route('exclusionconstraint', '/applications/{appid}/configurationkeys/{ckid}/exclusionconstraints/{ecid}')

    config.add_route('clients', '/applications/{appid}/clients')
    config.add_route('client', '/applications/{appid}/clients/{clientid}')
    config.add_route('experiments_for_client', '/applications/{appid}/clients/{clientid}/experiments')
    config.add_route('configurations_for_client', '/applications/{appid}clients/{clientid}/configurations')

    config.add_route('experiments', '/applications/{appid}/experiments')
    config.add_route('experiment', '/applications/{appid}/experiments/{expid}')
    config.add_route('clients_for_experiment', '/applications/{appid}/experiments/{expid}/clients')
    config.add_route('experimentgroups', '/applications/{appid}/experiments/{expid}/experimentgroups')
    config.add_route('experimentgroup', '/applications/{appid}/experiments/{expid}/experimentgroups/{expgroupid}')
