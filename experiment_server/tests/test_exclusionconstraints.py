from experiment_server.models.exclusionconstraints import ExclusionConstraint
from experiment_server.views.exclusionconstraints import ExclusionConstraints
from .base_test import BaseTest


# ---------------------------------------------------------------------------------
#                                DatabaseInterface
# ---------------------------------------------------------------------------------

class TestExclusionConstraints(BaseTest):
    def setUp(self):
        super(TestExclusionConstraints, self).setUp()
        self.init_database()
        self.init_databaseData()

    def test_getExConstraint(self):
        ec = ExclusionConstraint.get(1)
        assert ec.id == 1 and ec.first_configurationkey_id == 1 and ec.first_operator_id == 3

    def test_getAllExConstraints(self):
        ecsFromDB = ExclusionConstraint.all()
        assert len(ecsFromDB) == 2

    def test_destroyExConstraint(self):
        ec = ExclusionConstraint.get(1)
        ExclusionConstraint.destroy(ec)
        ecsFromDB = ExclusionConstraint.all()
        assert len(ecsFromDB) == 1

# ---------------------------------------------------------------------------------
#                                  REST-Inteface
# ---------------------------------------------------------------------------------

class TestExclusionConstraintsREST(BaseTest):

    exconst = {'id':1, 'first_configurationkey_id': 1, 'first_operator_id': 3,
               'first_value_a': None, 'first_value_b': None,
               'second_configurationkey_id': 2, 'second_operator_id': None,
               'second_value_a': None, 'second_value_b': None}

    exconst2 = {'id':2, 'first_configurationkey_id': 1, 'first_operator_id': 3,
               'first_value_a': None, 'first_value_b': None,
               'second_configurationkey_id': 2, 'second_operator_id': 2,
               'second_value_a': '2', 'second_value_b': None}

    def setUp(self):
        super(TestExclusionConstraintsREST, self).setUp()
        self.init_database()
        self.init_databaseData()
        self.req = self.dummy_request()

    def test_exclusionconstraints_GET(self):
        httpEcs = ExclusionConstraints(self.req)
        response = httpEcs.exclusionconstraints_GET()
        exconstraints = [self.exconst, self.exconst2]
        assert response == exconstraints

    def test_exclusionconstraints_GET_one(self):
        self.req.swagger_data = {'id': 1}
        httpRcs = ExclusionConstraints(self.req)
        response = httpRcs.exclusionconstraints_GET_one()
        assert response == self.exconst

    def test_exclusionconstraints_DELETE_one(self):
        self.req.swagger_data = {'id': 1}
        httpEcs = ExclusionConstraints(self.req)
        response = httpEcs.exclusionconstraints_DELETE_one()
        assert response == {}

        self.req.swagger_data = {'id': 3}
        httpEcs = ExclusionConstraints(self.req)
        response = httpEcs.exclusionconstraints_DELETE_one()
        assert response.status_code == 400