from experiment_server.models.operators import Operator
from experiment_server.views.operators import Operators
from .base_test import BaseTest


class TestOperators(BaseTest):

    op1 = {
        'id': 1,
        'math_value': '<=',
        'human_value': 'less or equal than'
    }
    op2 = {
        'id': 2,
        'math_value': '>=',
        'human_value': 'greater or equal than'
    }
    op3 = {
        'id': 3,
        'math_value': 'def',
        'human_value': 'must define'
    }

    def setUp(self):
        super(TestOperators, self).setUp()
        self.init_database()
        self.init_databaseData()
        self.req = self.dummy_request()

    def test_get_all_operators(self):
        operatorsFromDB = Operator.all()
        assert len(operatorsFromDB) == 10

    def test_get_operator(self):
        op1 = Operator.get(1)
        op3 = Operator.get(3)
        assert op1.id == 1 and op1.human_value == 'equals'
        assert op3.id == 3 and op3.math_value == '<'

# ---------------------------------------------------------------------------------
#                                  REST-Inteface
# ---------------------------------------------------------------------------------

    def test_GET_all_operators(self):
        httpOperators = Operators(self.req)
        response = httpOperators.GET_all_operators()
        operators = list(map(lambda _: _.as_dict(), Operator.all()))
        assert response == operators
