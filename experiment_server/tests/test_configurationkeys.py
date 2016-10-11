from .base_test import BaseTest
from ..models import (Application, ConfigurationKey)


class TestConfigurationKeys(BaseTest):
    def setUp(self):
        super(TestConfigurationKeys, self).setUp()
        self.init_database()
        self.init_databaseData()

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

    def test_deleteConfKey(self):
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

