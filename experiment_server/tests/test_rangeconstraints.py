from experiment_server.models.rangeconstraints import RangeConstraint
from experiment_server.views.rangeconstraints import RangeConstraints
from .base_test import BaseTest


# ---------------------------------------------------------------------------------
#                                DatabaseInterface
# ---------------------------------------------------------------------------------

class TestRangeConstraints(BaseTest):
    def setUp(self):
        super(TestRangeConstraints, self).setUp()
        self.init_database()
        self.init_databaseData()

    def test_getRangeConstraint(self):
        rc = RangeConstraint.get(1)
        assert rc.id == 1 and rc.configurationkey_id == 2 and rc.operator_id == 2 and rc.value == 1

    def test_getAllRangeConstraints(self):
        rconstraintsFromDB = RangeConstraint.all()
        assert len(rconstraintsFromDB) == 2

    def test_destroyExConstraint(self):
        rc = RangeConstraint.get(1)
        RangeConstraint.destroy(rc)
        appsFromDB = RangeConstraint.all()
        assert len(appsFromDB) == 1

# ---------------------------------------------------------------------------------
#                                  REST-Inteface
# ---------------------------------------------------------------------------------

class TestRangeConstraintsREST(BaseTest):
    def setUp(self):
        super(TestRangeConstraintsREST, self).setUp()
        self.init_database()
        self.init_databaseData()
        self.req = self.dummy_request()

    def test_rangeconstraints_GET(self):
        #TODO: Write test
        assert 1 == 1

    def test_rangecontraints_DELETE_one(self):
        #TODO: Write test
        assert 1 == 1

    def test_rangecontraints_POST(self):
        #TODO: Write test
        assert 1 == 1

    def test_rangeconstraints_for_configuratinkey_DELETE(self):
        #TODO: Write test
        assert 1 == 1
