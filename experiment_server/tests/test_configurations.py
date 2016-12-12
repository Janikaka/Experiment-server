import datetime
from .base_test import BaseTest
from ..models import (Application, Configuration, ConfigurationKey, Experiment, ExperimentGroup)
from ..views.configurations import Configurations


def strToDatetime(date):
    return datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------------------------
#                                DatabaseInterface
# ---------------------------------------------------------------------------------

class TestConfigurations(BaseTest):

    def setUp(self):
        super(TestConfigurations, self).setUp()
        self.init_database()
        self.init_databaseData()

    def test_createConfiguration(self):
        expgroup1 = self.dbsession.query(ExperimentGroup).filter(ExperimentGroup.id == 1).one()
        conf_count_before = Configuration.query().count()

        conf = Configuration(id=87, key='v1', value=0.5, experimentgroup=expgroup1)
        Configuration.save(conf)

        conf_count_now = Configuration.query().count()

        assert conf_count_now > conf_count_before
        assert Configuration.get_by('id', 87) is not None

    def test_deleteConfiguration(self):
        conf1 = self.dbsession.query(Configuration).filter_by(id=1).one()
        expgroup = conf1.experimentgroup
        assert conf1 in expgroup.configurations
        self.DB.delete_configuration(conf1.id)
        assert conf1 not in expgroup.configurations
        conf1 = self.dbsession.query(Configuration).filter_by(id=1).all()
        assert [] == conf1

    def test_getConfsForExperimentgroup(self):
        configurations = self.DB.get_confs_for_experimentgroup(1)
        conf1 = self.dbsession.query(Configuration).filter_by(id=1).one()
        conf2 = self.dbsession.query(Configuration).filter_by(id=2).one()

        assert configurations == [conf1, conf2]

    def test_getTotalConfigurationForClient(self):
        configurations = self.DB.get_total_configuration_for_client(1)
        conf1 = self.dbsession.query(Configuration).filter_by(id=1).one()
        conf2 = self.dbsession.query(Configuration).filter_by(id=2).one()

        assert configurations == [conf1, conf2]

# ---------------------------------------------------------------------------------
#                                  REST-Inteface
# ---------------------------------------------------------------------------------

class TestConfigurationsREST(BaseTest):

    def setUp(self):
        super(TestConfigurationsREST, self).setUp()
        self.init_database()
        self.init_databaseData()
        self.req = self.dummy_request()

    def test_configurations_GET(self):
        expgroup_id = 1
        exp_id = 1
        app_id = 1

        configurations = Configuration.query().join(ExperimentGroup, Experiment, Application)\
            .filter(ExperimentGroup.id == expgroup_id, Experiment.id == exp_id, Application.id == app_id).all()

        expected_result = list(map(lambda _: _.as_dict(), configurations))

        self.req.swagger_data = {'appid': app_id, 'expid': exp_id, 'expgroupid': expgroup_id}
        httpConfs = Configurations(self.req)
        response = httpConfs.configurations_GET()

        assert response == expected_result

    def test_configurations_GET_expgroup_must_belong_to_experiment(self):
        expgroup_id = 1
        exp_id = 2
        app_id = 1

        expected_result = []

        self.req.swagger_data = {'appid': app_id, 'expid': exp_id, 'expgroupid': expgroup_id}
        httpConfs = Configurations(self.req)
        response = httpConfs.configurations_GET()

        assert response == expected_result

    def test_configurations_GET_experiment_must_belong_to_application(self):
        expgroup_id = 1
        exp_id = 1
        app_id = 2

        expected_result = []

        self.req.swagger_data = {'appid': app_id, 'expid': exp_id, 'expgroupid': expgroup_id}
        httpConfs = Configurations(self.req)
        response = httpConfs.configurations_GET()

        assert response == expected_result

    def test_configurations_POST(self):

        expgroup_id = 1
        exp_id = 1
        app_id = 1

        confkey = ConfigurationKey.get(1)
        #print(confkey.as_dict())
        expected_result = Configuration(experimentgroup_id=exp_id, key=confkey.name, value=False)
        count_before = Configuration.query().count()

        self.req.swagger_data = {'appid': app_id, 'expid': exp_id, 'expgroupid': expgroup_id,
                                 'configuration': expected_result}
        httpConfs = Configurations(self.req)
        response = httpConfs.configurations_POST()
        count_now = Configuration.query().count()

        assert response == expected_result.as_dict()
        assert count_now > count_before

    def test_configurations_POST_expgroup_belongs_to_experiment(self):

        expgroup_id = 1
        exp_id = 2
        app_id = 1

        confkey = ConfigurationKey.get(1)
        #print(confkey.as_dict())
        configuration = Configuration(experimentgroup_id=exp_id, key=confkey.name, value=False)
        count_before = Configuration.query().count()

        self.req.swagger_data = {'appid': app_id, 'expid': exp_id, 'expgroupid': expgroup_id,
                                 'configuration': configuration}
        httpConfs = Configurations(self.req)
        response = httpConfs.configurations_POST()
        count_now = Configuration.query().count()
        expected_status = 400

        assert response.status_code == expected_status
        assert count_now == count_before

    def test_configurations_POST_experiment_belongs_to_application(self):

        expgroup_id = 1
        exp_id = 1
        app_id = 2

        confkey = ConfigurationKey.get(1)
        #print(confkey.as_dict())
        configuration = Configuration(experimentgroup_id=exp_id, key=confkey.name, value=False)
        count_before = Configuration.query().count()

        self.req.swagger_data = {'appid': app_id, 'expid': exp_id, 'expgroupid': expgroup_id,
                                 'configuration': configuration}
        httpConfs = Configurations(self.req)
        response = httpConfs.configurations_POST()
        count_now = Configuration.query().count()
        expected_status = 400

        assert response.status_code == expected_status
        assert count_now == count_before

    def test_configurations_POST_key_exists(self):
        expgroup_id = 1
        exp_id = 1
        app_id = 1

        expected_result = Configuration(experimentgroup_id=exp_id, key='nonexistent key', value=False)
        count_before = Configuration.query().count()

        self.req.swagger_data = {'appid': app_id, 'expid': exp_id, 'expgroupid': expgroup_id,
                                 'configuration': expected_result}
        httpConfs = Configurations(self.req)
        response = httpConfs.configurations_POST()
        count_now = Configuration.query().count()
        expected_status = 400

        assert response.status_code == expected_status
        assert count_now == count_before

    def test_configurations_POST_value_is_valid_is_right_type(self):
        expgroup_id = 1
        exp_id = 1
        app_id = 1

        confkey = ConfigurationKey.get(1)
        # print(confkey.as_dict())
        expected_result = Configuration(experimentgroup_id=exp_id, key=confkey.name, value='Lentävä puliukko')
        count_before = Configuration.query().count()

        self.req.swagger_data = {'appid': app_id, 'expid': exp_id, 'expgroupid': expgroup_id,
                                 'configuration': expected_result}
        httpConfs = Configurations(self.req)
        response = httpConfs.configurations_POST()
        count_now = Configuration.query().count()
        expected_status = 400

        assert response.status_code == expected_status
        assert count_now == count_before
