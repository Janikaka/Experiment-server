import datetime
from .base_test import BaseTest
from ..models import (ExperimentGroup, Configuration)


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
