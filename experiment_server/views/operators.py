from pyramid.view import view_config, view_defaults
from experiment_server.models.operators import Operator
from experiment_server.utils.log import print_log
from .webutils import WebUtils
import datetime

@view_defaults(renderer='json')
class Applications(WebUtils):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='operators', request_method="GET")
    def GET_all_operators(self):
        return list(map(lambda _: _.as_dict(), Operator.all()))
