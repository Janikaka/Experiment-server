from .base_test import BaseTest
from ..models import (Application, ConfigurationKey)
from experiment_server.views.configurationkeys import ConfigurationKeys


# ---------------------------------------------------------------------------------
#                                DatabaseInterface
# ---------------------------------------------------------------------------------

class TestConfigurationKeys(BaseTest):

    def setUp(self):
        super(TestConfigurationKeys, self).setUp()
        self.init_database()
        self.init_databaseData()
        self.req = self.dummy_request()

        self.confkey = {
            'id': 1, 'application_id': 1,
            'type': 'boolean', 'name': 'highscore'
        }

        self.confkey2 = {
            'id': 2, 'application_id': 1,
            'type': 'integer', 'name': 'difficulty'
        }

    def test_createConfKey(self):
        ckeysFromDB = ConfigurationKey.all()
        appsFromDB = Application.all()
        ck1 = {
            'id': 1,
            'application': appsFromDB[0],
            'name': 'highscore',
            'type': 'boolean'
        }
        ck2 = {
            'id': 2,
            'application': appsFromDB[0],
            'name': 'difficulty',
            'type': 'integer'
        }
        confkeys = [ck1, ck2]

        for i in range(len(ckeysFromDB)):
            for key in confkeys[i]:
                assert getattr(ckeysFromDB[i], key) == confkeys[i][key]

    def test_getAllConfKeys(self):
        ckeysFromDB = ConfigurationKey.all()
        assert len(ckeysFromDB) == 2

    def test_getConfKey(self):
        ck1 = ConfigurationKey.get(1)
        ck2 = ConfigurationKey.get(2)
        assert ck1.id == 1 and ck1.name == 'highscore' and \
               ck1.application.id == 1
        assert ck2.id == 2 and ck2.name == 'difficulty' and \
               ck2.application.id == 1

    def test_destroyConfKey(self):
        ck1 = ConfigurationKey.get(1)
        ConfigurationKey.destroy(ck1)
        ckeysFromDB = ConfigurationKey.all()
        ck2 = ConfigurationKey.get(2)
        assert ckeysFromDB == [ck2]
        assert len(ckeysFromDB) == 1

    def test_saveConfKey(self):
        confk3 = ConfigurationKey(application=Application.get(2), name='speed', type='double')
        ConfigurationKey.save(confk3)
        ckeysFromDB = ConfigurationKey.all()
        assert len(ckeysFromDB) == 3

    def test_getAppsConfKeys(self):
        assert len(Application.get(1).configurationkeys) == 2
        ck = Application.get(1).configurationkeys[0]
        assert ck.name == 'highscore'

# ---------------------------------------------------------------------------------
#                                  REST-Inteface
# ---------------------------------------------------------------------------------

class TestConfigurationKeysREST(BaseTest):
    def setUp(self):
        super(TestConfigurationKeysREST, self).setUp()
        self.init_database()
        self.init_databaseData()
        self.req = self.dummy_request()

    def test_configurationkeys_GET_one(self):
        self.req.swagger_data = {'id': 1}
        httpCkeys = ConfigurationKeys(self.req)
        response = httpCkeys.configurationkeys_GET_one()
        assert response == self.confkey

    def test_configurationkeys_GET(self):
        httpCkeys = ConfigurationKeys(self.req)
        response = httpCkeys.configurationkeys_GET()
        confkeys = [self.confkey, self.confkey2]
        assert response == confkeys

    def test_configurationkeys_PUT_one(self):
        #TODO: Write test
        assert 1 == 1

    def test_configurationkeys_DELETE_one(self):
        self.req.swagger_data = {'id': 1}
        httpCkeys = ConfigurationKeys(self.req)
        response = httpCkeys.configurationkeys_DELETE_one()
        assert response == {}

        self.req.swagger_data = {'id': 3}
        httpCkeys = ConfigurationKeys(self.req)
        response = httpCkeys.configurationkeys_DELETE_one()
        assert response.status_code == 400

    def test_rangeconstraints_for_confkey_GET(self):
        self.req.swagger_data = {'id': 1}
        httpCkeys = ConfigurationKeys(self.req)
        response = httpCkeys.rangeconstraints_for_confkey_GET()
        rconstraints = [{'id': 1, 'configurationkey_id': 2, 'operator_id': 2, 'value': 1},
                        {'id': 2, 'configurationkey_id': 2, 'operator_id': 1, 'value': 5}]
        assert response == []
        self.req.swagger_data = {'id': 2}
        httpCkeys = ConfigurationKeys(self.req)
        response = httpCkeys.rangeconstraints_for_confkey_GET()
        assert response == rconstraints

    def test_configurationkeys_POST(self):
        #TODO: Write test
        assert 1 == 1

    def test_configurationkeys_for_application_DELETE(self):
        #TODO: Write test
        assert 1 == 1
