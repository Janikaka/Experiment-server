from experiment_server.models.rangeconstraints import RangeConstraint
from experiment_server.views.rangeconstraints import RangeConstraints
from experiment_server.models.configurationkeys import ConfigurationKey
from .base_test import BaseTest


# ---------------------------------------------------------------------------------
#                                DatabaseInterface
# ---------------------------------------------------------------------------------

class TestRangeConstraints(BaseTest):
    def setUp(self):
        super(TestRangeConstraints, self).setUp()
        self.init_database()
        self.init_databaseData()

    def test_get_rangeconstraint(self):
        rc = RangeConstraint.get(1)
        assert rc.id == 1 and rc.configurationkey_id == 2 and rc.operator_id == 2 and rc.value == 1

    def test_get_all_rangeconstraints(self):
        rcsFromDB = RangeConstraint.all()
        assert len(rcsFromDB) == 2

    def test_destroy_rangeconstraint(self):
        rc = RangeConstraint.get(1)
        RangeConstraint.destroy(rc)
        rcsFromDB = RangeConstraint.all()
        assert len(rcsFromDB) == 1

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
        httpRcs = RangeConstraints(self.req)
        response = httpRcs.rangeconstraints_GET()
        rc1 = {'id': 1, 'configurationkey_id': 2, 'operator_id': 2, 'value': 1}
        rc2 = {'id': 2, 'configurationkey_id': 2, 'operator_id': 1, 'value': 5}
        rcs = [rc1, rc2]
        assert response == rcs

    def test_rangecontraints_DELETE_one(self):
        self.req.swagger_data = {'id': 1}
        httpRcs = RangeConstraints(self.req)
        response = httpRcs.rangecontraints_DELETE_one()
        assert response == {}

        self.req.swagger_data = {'id': 3}
        httpRcs = RangeConstraints(self.req)
        response = httpRcs.rangecontraints_DELETE_one()
        assert response.status_code == 400

    def test_rangecontraints_POST(self):
        #TODO: Write post test
        assert 1 == 0

    def test_rangeconstraints_for_configuratinkey_DELETE(self):
        self.req.swagger_data = {'id': 2}
        httpRcs = RangeConstraints(self.req)
        assert len(ConfigurationKey.get(2).rangeconstraints) == 2
        response = httpRcs.rangeconstraints_for_configuratinkey_DELETE()
        assert len(ConfigurationKey.get(2).rangeconstraints) == 0
        assert response == {}
        self.req.swagger_data = {'id': 3}
        httpRcs = RangeConstraints(self.req)
        response = httpRcs.rangeconstraints_for_configuratinkey_DELETE()
        assert response.status_code == 400
