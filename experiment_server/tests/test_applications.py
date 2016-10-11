from experiment_server.models.applications import Application
from .base_test import BaseTest


class TestApplications(BaseTest):
    def setUp(self):
        super(TestApplications, self).setUp()
        self.init_database()
        self.init_databaseData()

    def test_createApp(self):
        appsFromDB = Application.all()
        app1 = {
            'id': 1,
            'name': 'App 1'
        }
        app2 = {
            'id': 2,
            'name': 'App 2'
        }
        apps = [app1, app2]

        for i in range(len(appsFromDB)):
            for key in apps[i]:
                assert getattr(appsFromDB[i], key) == apps[i][key]

    def test_getAllApps(self):
        appsFromDB = Application.all()
        assert len(appsFromDB) == 2

    def test_getApp(self):
        app1 = Application.get(1)
        app2 = Application.get(2)
        assert app1.id == 1 and app1.name == 'App 1'
        assert app2.id == 2 and app2.name == 'App 2'

    def test_saveApp(self):
        app = Application(name='App 3')
        Application.save(app)
        appsFromDB = Application.all()
        assert len(appsFromDB) == 3

    def test_deleteApp(self):
        app1 = Application.get(1)
        Application.destroy(app1)
        appsFromDB = Application.all()
        app2 = Application.get(2)
        assert appsFromDB == [app2]
        assert len(appsFromDB) == 1
