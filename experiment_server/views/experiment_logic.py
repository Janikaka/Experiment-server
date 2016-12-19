from pyramid.view import view_config, view_defaults
from experiment_server.models.operators import Operator
from experiment_server.utils.log import print_log
from .webutils import WebUtils
from ..experiment_logic.experiment_logic_selector import ExperimentLogicSelector
import datetime


@view_defaults(renderer='json')
class Logic(WebUtils):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='logic', request_method="GET")
    def GET_all_logic(self):
        """Returns all experiment distribution strategies as a list"""
        return ExperimentLogicSelector().get_valid_experiment_logics()
