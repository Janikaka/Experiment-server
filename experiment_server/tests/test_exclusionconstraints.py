from experiment_server.models.configurationkeys import ConfigurationKey
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

    def test_get_exclusionconstraint(self):
        ec = ExclusionConstraint.get(1)
        assert ec.id == 1 and ec.first_configurationkey_id == 1 and ec.first_operator_id == 3

    def test_get_all_exclusionconstraints(self):
        ecsFromDB = ExclusionConstraint.all()
        assert len(ecsFromDB) == 2

    def test_destroy_exclusionconstraint(self):
        ec = ExclusionConstraint.get(1)
        ExclusionConstraint.destroy(ec)
        ecsFromDB = ExclusionConstraint.all()
        assert len(ecsFromDB) == 1

# ---------------------------------------------------------------------------------
#                                  REST-Inteface
# ---------------------------------------------------------------------------------

exconst = {'id': 1, 'first_configurationkey_id': 1, 'first_operator_id': 3,
           'first_value': [None, None],
           'second_configurationkey_id': 2, 'second_operator_id': None,
           'second_value': [2, None]}

exconst2 = {'id': 2, 'first_configurationkey_id': 1, 'first_operator_id': 3,
            'first_value': [1, 3],
            'second_configurationkey_id': 2, 'second_operator_id': 2,
            'second_value': ['2', None]}
exconstraints = [exconst, exconst2]

class TestExclusionConstraintsREST(BaseTest):

    exconst = {'id':1, 'first_configurationkey_id': 1, 'first_operator_id': 3,
               'first_value': [None, None],
               'second_configurationkey_id': 2, 'second_operator_id': None,
               'second_value': [None, None]}

    exconst2 = {'id':2, 'first_configurationkey_id': 1, 'first_operator_id': 3,
                'first_value': [None, None],
               'second_configurationkey_id': 2, 'second_operator_id': 2,
                'second_value': ['2', None]}

    def setUp(self):
        super(TestExclusionConstraintsREST, self).setUp()
        self.init_database()
        self.init_databaseData()
        self.req = self.dummy_request()

    def test_exclusionconstraints_GET(self):
        self.req.swagger_data = {'appid':1}
        httpEcs = ExclusionConstraints(self.req)
        response = httpEcs.exclusionconstraints_GET()
        exconstraints = [self.exconst, self.exconst2]
        assert response == exconstraints

    def test_exclusionconstraints_GET_one(self):
        self.req.swagger_data = {'appid': 1, 'ecid': 1}
        httpRcs = ExclusionConstraints(self.req)
        response = httpRcs.exclusionconstraints_GET_one()
        assert response == self.exconst

    def test_exclusionconstraints_DELETE_one(self):
        self.req.swagger_data = {'appid': 1, 'ecid': 1}
        httpEcs = ExclusionConstraints(self.req)
        response = httpEcs.exclusionconstraints_DELETE_one()
        assert response == {}

    def test_exclusionconstraints_POST_configurationkey_type_is_valid(self):
        wrong_type_value_to_first = 42
        correct_type_value_to_second = wrong_type_value_to_first
        ckey1 = ConfigurationKey(id=467, application_id=1, name='tosi juttu', type='boolean')
        ConfigurationKey.save(ckey1)
        ckey2 = ConfigurationKey(id=468, application_id=1, name='elämän tarkoitus', type='integer')
        ConfigurationKey.save(ckey2)

        exclusion = {'id': 467, 'first_configurationkey_id': 467, 'first_operator_id': 1,
               'first_value': [wrong_type_value_to_first, None],
               'second_configurationkey_id': 468, 'second_operator_id': 1,
               'second_value': [correct_type_value_to_second, None]}
        self.req.swagger_data = {'appid': 1, 'exclusionconstraint': exclusion}
        httpEcs = ExclusionConstraints(self.req)
        response = httpEcs.exclusionconstraints_POST()
        expected_status = 400

        assert response.status_code == expected_status