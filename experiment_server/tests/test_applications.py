from experiment_server.models.applications import Application
from experiment_server.views.applications import Applications
from .base_test import BaseTest


# ---------------------------------------------------------------------------------
#                                DatabaseInterface
# ---------------------------------------------------------------------------------

class TestApplications(BaseTest):
    def setUp(self):
        super(TestApplications, self).setUp()
        self.init_database()
        self.init_databaseData()

    def test_create_app(self):
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

    def test_get_all_apps(self):
        appsFromDB = Application.all()
        assert len(appsFromDB) == 2

    def test_get_app(self):
        app1 = Application.get(1)
        app2 = Application.get(2)
        assert app1.id == 1 and app1.name == 'App 1'
        assert app2.id == 2 and app2.name == 'App 2'

    def test_save_app(self):
        app = Application(name='App 3')
        Application.save(app)
        appsFromDB = Application.all()
        assert len(appsFromDB) == 3

    def test_destroy_app(self):
        app1 = Application.get(1)
        Application.destroy(app1)
        appsFromDB = Application.all()
        app2 = Application.get(2)
        assert appsFromDB == [app2]
        assert len(appsFromDB) == 1

    def test_get_confkeys_of_app(self):
        assert len(Application.get(1).configurationkeys) == 2
        ck = Application.get(1).configurationkeys[0]
        assert ck.name == 'highscore'

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
        self.req.matchdict = {'id': 1}
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
        self.req.matchdict = {'id': 1}
        httpApps = Applications(self.req)
        response = httpApps.applications_DELETE_one()
        assert response == {}

        self.req.matchdict = {'id': 3}
        response = httpApps.applications_DELETE_one()
        assert response.status_code == 400

    def test_applications_POST(self):
        self.req.matchdict = {'application': Application(name='App 3')}
        httpApps = Applications(self.req)
        response = httpApps.applications_POST()
        app = {'id': 3, 'name': 'App 3'}
        assert response == app

    def test_data_for_app_GET(self):
        self.req.matchdict = {'id': 1}
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

    def test_application_routes(self):
        assert self.req.route_url('application', id=1) == 'http://example.com/applications/1'
        assert self.req.route_url('applications') == 'http://example.com/applications'
