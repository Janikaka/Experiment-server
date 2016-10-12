from experiment_server.models.applications import Application
from experiment_server.views.applications import Applications
from .base_test import BaseTest


class TestApplications(BaseTest):
    def setUp(self):
        super(TestApplications, self).setUp()
        self.init_database()
        self.init_databaseData()
        self.req = self.dummy_request()

# ---------------------------------------------------------------------------------
#                                DatabaseInterface
# ---------------------------------------------------------------------------------

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

    def test_destroyApp(self):
        app1 = Application.get(1)
        Application.destroy(app1)
        appsFromDB = Application.all()
        app2 = Application.get(2)
        assert appsFromDB == [app2]
        assert len(appsFromDB) == 1

# ---------------------------------------------------------------------------------
#                                  REST-Inteface
# ---------------------------------------------------------------------------------

class TestApplicationsREST(BaseTest):

    def setUp(self):
        super(TestApplicationsREST, self).setUp()
        self.init_database()
        self.init_databaseData()
        self.req = self.dummy_request()

    def test_applications_GET_one(self):
        self.req.swagger_data = {'id': 1}
        httpApps = Applications(self.req)
        response = httpApps.applications_GET_one()
        app = {'id': 1, 'name': 'App 1'}
        assert response == app

    def test_applications_GET(self):
        httpApps = Applications(self.req)
        response = httpApps.applications_GET()
        apps = [{'id': 1, 'name': 'App 1'}, {'id': 2, 'name': 'App 2'}]
        assert response == apps

    def test_applications_DELETE_one(self):
        self.req.swagger_data = {'id': 1}
        httpApps = Applications(self.req)
        response = httpApps.applications_DELETE_one()
        assert response == {}

        self.req.swagger_data = {'id': 3}
        httpApps = Applications(self.req)
        response = httpApps.applications_DELETE_one()
        assert response.status_code == 400

    def test_applications_POST(self):
        self.req.swagger_data = {'application': {'name': 'App 3'}}
        httpApps = Applications(self.req)
        response = httpApps.applications_POST()
        app = {'id': 3, 'name': 'App 3'}
        assert response == app

    def test_configurationkeys_for_application_GET(self):
        self.req.swagger_data = {'id': 1}
        httpApps = Applications(self.req)
        response = httpApps.configurationkeys_for_application_GET()
        ckeys = [{'id': 1, 'application_id':1, 'name': 'highscore', 'type': 'boolean'},
        {'id': 2, 'application_id': 1,  'name': 'difficulty', 'type': 'integer'}]
        assert response == ckeys

    def test_rangeconstraints_for_app_GET(self):
        self.req.swagger_data = {'id': 1}
        httpApps = Applications(self.req)
        response = httpApps.rangeconstraints_for_app_GET()
        rconstraints = [{'id': 1, 'configurationkey_id': 2, 'operator_id': 2, 'value': 1},
                        {'id': 2, 'configurationkey_id': 2, 'operator_id': 1, 'value': 5}]
        assert response == rconstraints
        self.req.swagger_data = {'id': 2}
        httpApps = Applications(self.req)
        response = httpApps.rangeconstraints_for_app_GET()
        assert response == []

    def test_data_for_app_GET(self):
        self.req.swagger_data = {'id': 1}
        httpApps = Applications(self.req)
        response = httpApps.data_for_app_GET()
        app_data = {
            'id': 1,
            'name': 'App 1',
            'rangeconstraints': [
                {
                    'id': 1,
                    'configurationkey_id': 2,
                    'operator_id': 2,
                    'value': 1
                },
                {
                    'id': 2,
                    'configurationkey_id': 2,
                    'operator_id': 1,
                    'value': 5
                }
            ],
            'configurationkeys': [
                {
                    'id': 1,
                    'application_id': 1,
                    'type': 'boolean',
                    'name': 'highscore'
                },
                {
                    'id': 2,
                    'application_id': 1,
                    'type': 'integer',
                    'name': 'difficulty'
                }
            ],
        }

        assert response == app_data

