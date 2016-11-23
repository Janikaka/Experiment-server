from experiment_server.models.applications import Application
from experiment_server.models.rangeconstraints import RangeConstraint
from experiment_server.views.applications import Applications
from .base_test import BaseTest
import uuid


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

    def test_can_set_apikey(self):
        apikey = str(uuid.uuid4())
        app = Application(name='App with UUID', apikey=str(uuid.uuid4()))
        app = Application.save(app)

        expected = Application.get_by('apikey', apikey)

        assert expected == app

    def test_apikey_is_unique(self):
        apikey = str(uuid.uuid4())
        app = Application(name='App with UUID', apikey=str(apikey))
        app = Application.save(app)

        app = Application(name='Another app with UUID', apikey=str(apikey))
        was_added = True
        try:
            Application.save(app)
        except Exception as e:
            was_added = False
            pass

        assert not was_added

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
        expected = Application.get(1).as_dict()
        assert response == expected

    def test_applications_GET_one_apikey_not_none(self):
        self.req.swagger_data = {'id': 1}
        httpApps = Applications(self.req)
        response = httpApps.applications_GET_one()
        assert response['apikey'] != None

    def test_applications_GET(self):
        httpApps = Applications(self.req)
        response = httpApps.applications_GET()
        expected = list(map(lambda _: _.as_dict(), Application.all()))
        assert response == expected

    def test_applications_DELETE_one(self):
        self.req.swagger_data = {'id': 1}
        httpApps = Applications(self.req)
        response = httpApps.applications_DELETE_one()
        assert response == {}

        self.req.swagger_data = {'id': 3}
        response = httpApps.applications_DELETE_one()
        assert response.status_code == 400

    def test_applications_POST(self):
        self.req.swagger_data = {'application': Application(name='App 3')}
        httpApps = Applications(self.req)
        response = httpApps.applications_POST()

        expected = Application.get_by('name', 'App 3').as_dict()
        assert response == expected

    def test_applications_POST_apikey_is_set(self):
        self.req.swagger_data = {'application': Application(name='App 3')}
        httpApps = Applications(self.req)
        response = httpApps.applications_POST()

        expected = Application.get_by('name', 'App 3').as_dict()
        assert expected['apikey'] is not None

    def test_data_for_app_GET(self):
        from toolz import assoc, concat
        self.req.swagger_data = {'id': 1}
        httpApps = Applications(self.req)
        response = httpApps.data_for_app_GET()

        app = Application.get(1)
        configurationkeys = app.configurationkeys
        ranges = list(concat(list(map(lambda _: _.rangeconstraints, configurationkeys))))

        app_data = app.as_dict()
        app_data = assoc(app_data, 'configurationkeys', list(map(lambda _: _.as_dict(), configurationkeys)))
        app_data = assoc(app_data, 'rangeconstraints', list(map(lambda _: _.as_dict(), ranges)))
        app_data = assoc(app_data, 'exclusionconstraints', list(map(lambda _: _.as_dict(), httpApps.get_app_exclusionconstraints(1))))

        assert response == app_data

    def test_application_routes(self):
        assert self.req.route_url('application', id=1) == 'http://example.com/applications/1'
        assert self.req.route_url('applications') == 'http://example.com/applications'
