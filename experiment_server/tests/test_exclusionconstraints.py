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
        appsFromDB = ExclusionConstraint.all()
        assert len(appsFromDB) == 1

    def test_destroyExConstraint(self):
        ec = ExclusionConstraint.get(1)
        ExclusionConstraint.destroy(ec)
        appsFromDB = ExclusionConstraint.all()
        assert len(appsFromDB) == 0

# ---------------------------------------------------------------------------------
#                                  REST-Inteface
# ---------------------------------------------------------------------------------

class TestExclusionConstraintsREST(BaseTest):
    def setUp(self):
        super(TestExclusionConstraintsREST, self).setUp()
        self.init_database()
        self.init_databaseData()
        self.req = self.dummy_request()

    def test_exclusionconstraints_GET(self):
        #TODO: Write test
        assert 1 == 1

    def test_exclusionconstraints_GET_one(self):
        #TODO: Write test
        assert 1 == 1

    def test_exclusionconstraints_DELETE_one(self):
        #TODO: Write test
        assert 1 == 1