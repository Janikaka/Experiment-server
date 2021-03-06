from pyramid.view import view_config, view_defaults
from experiment_server.models.operators import Operator
from experiment_server.utils.log import print_log
from .webutils import WebUtils
from experiment_server.utils.configuration_tools import get_operators
import datetime


@view_defaults(renderer='json')
class Operators(WebUtils):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='operators', request_method="GET")
    def GET_all_operators(self):
        """ Retuns all operators as a list"""
        return list(map(lambda _: _.as_dict(), get_operators()))
