from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.include('.models')
    config.include('.routes')
    config.add_route('experiments', '/experiments')
    config.add_route('experiment_metadata', '/experiments/{id}/metadata')
    config.add_route('experiment', '/experiments/{id}')
    config.add_route('configurations', '/configurations')
    config.add_route('users', '/users')
    config.add_route('users_for_experiment', '/experiments/{id}/users')
    config.add_route('experiments_for_user', '/users/{id}/experiments')
    config.add_route('events', '/events')
    config.add_route('user', '/users/{id}')
    config.add_route('experiment_data', '/experiments/{id}/data')

    config.add_route('hello', '/hello/{param}')
    config.scan()
    return config.make_wsgi_app()



#curl -H "Content-Type: application/json" -X POST -d '{"name":"First experiment","experimentgroups":["group A", "group B"]}' http://0.0.0.0:6543/experiments















