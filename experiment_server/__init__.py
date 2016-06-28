from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.include('.models')
    config.include('.routes')
    config.scan()
    return config.make_wsgi_app()



#curl -H "Content-Type: application/json" -X DELETE -d '' http://0.0.0.0:6543/experiments/1

#curl -H "Content-Type: application/json" -X POST -d '{"name":"First experiment","experimentgroups":["group A", "group B"]}' http://0.0.0.0:6543/experiments














