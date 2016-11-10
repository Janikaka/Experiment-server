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
        configurationsFromDB = self.dbsession.query(Configuration).all()
        expgroup1 = self.dbsession.query(ExperimentGroup).filter_by(id=1).one()
        expgroup2 = self.dbsession.query(ExperimentGroup).filter_by(id=2).one()
        conf1 = {'key': 'v1',
                 'value': 0.5,
                 'experimentgroup': expgroup1
                 }
        conf2 = {'key': 'v2',
                 'value': True,
                 'experimentgroup': expgroup1
                 }
        conf3 = {'key': 'v1',
                 'value': 1.0,
                 'experimentgroup': expgroup2
                 }
        conf4 = {'key': 'v2',
                 'value': False,
                 'experimentgroup': expgroup2
                 }
        confs = [conf1, conf2, conf3, conf4]

        for i in range(len(configurationsFromDB)):
            for key in confs[i]:
                assert getattr(configurationsFromDB[i], key) == confs[i][key]

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
