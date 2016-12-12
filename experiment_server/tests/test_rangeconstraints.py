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
        self.req.swagger_data = {'appid':1, 'ckid':2, 'rcid': 1}
        httpRcs = RangeConstraints(self.req)
        response = httpRcs.rangecontraints_DELETE_one()
        assert response == {}

    def test_rangecontraints_DELETE_one_nonexistent(self):
        self.req.swagger_data = {'appid':1, 'ckid':2, 'rcid': 3}
        httpRcs = RangeConstraints(self.req)
        response = httpRcs.rangecontraints_DELETE_one()
        assert response.status_code == 400

    def test_rangecontraints_POST(self):
        self.req.swagger_data = {
            'appid': 1,
            'ckid': 2,
            'rangeconstraint': RangeConstraint(operator_id=4, value=10)}
        httpCkeys = RangeConstraints(self.req)
        response = httpCkeys.rangecontraints_POST()
        rc = RangeConstraint.query()\
            .filter(RangeConstraint.configurationkey_id == 2,
                RangeConstraint.operator_id==4,
                RangeConstraint.value==10)\
            .one().as_dict()
        assert response == rc

    def test_rangeconstraints_POST_is_valid_operator(self):
        expected_count = RangeConstraint.query().count()
        self.req.swagger_data = {
            'appid': 1,
            'ckid': 2,
            'rangeconstraint': RangeConstraint(operator_id=1, value=10)}
        httpCkeys = RangeConstraints(self.req)
        response = httpCkeys.rangecontraints_POST()

        expected_status = 400
        count_now = RangeConstraint.query().count()

        assert count_now == expected_count
        assert response.status_code == expected_status

    def test_rangeconstraints_POST_is_valid_value(self):
        expected_count = RangeConstraint.query().count()
        self.req.swagger_data = {
            'appid': 1,
            'ckid': 2,
            'rangeconstraint': RangeConstraint(operator_id=2, value="Herpiderp")}
        httpCkeys = RangeConstraints(self.req)
        response = httpCkeys.rangecontraints_POST()

        expected_status = 400
        count_now = RangeConstraint.query().count()

        assert count_now == expected_count
        assert response.status_code == expected_status

    def test_rangeconstraints_for_configuratinkey_DELETE(self):
        self.req.swagger_data = {'appid':1, 'ckid': 2}
        httpRcs = RangeConstraints(self.req)
        response = httpRcs.rangeconstraints_for_configuratinkey_DELETE()
        assert len(ConfigurationKey.get(2).rangeconstraints) == 0 and response == {}

    def test_rangeconstraints_for_configuratinkey_DELETE_incorrect_confkey_id(self):
        self.req.swagger_data = {'appid':1, 'ckid': 3}
        httpRcs = RangeConstraints(self.req)
        response = httpRcs.rangeconstraints_for_configuratinkey_DELETE()
        assert response.status_code == 400

    def test_rangeconstraints_GET_with_incorrect_confkeyid(self):
        self.req.swagger_data = {'appid': 1, 'ckid': 1}
        httpRcs = RangeConstraints(self.req)
        response = httpRcs.rangeconstraints_GET()
        assert response == []

    def test_rangeconstraints_GET(self):
        httpRcs = RangeConstraints(self.req)
        self.req.swagger_data = {'appid': 1, 'ckid': 2}
        response = httpRcs.rangeconstraints_GET()

        expected = RangeConstraint.query().filter(RangeConstraint.configurationkey_id == 2)
        expected = list(map(lambda _: _.as_dict(), expected))

        assert response == expected
