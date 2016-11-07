import datetime
from .base_test import BaseTest
from ..models import (Configuration, ExperimentGroup, User)


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

    # Such method no longer exists. Either remove the test or create such method.
    def test_deleteConfiguration(self):
        conf1 = self.dbsession.query(Configuration).filter_by(id=1).one()
        expgroup = conf1.experimentgroup
        assert conf1 in expgroup.configurations
        conf1 = Configuration.destroy(conf1)
        assert conf1 not in expgroup.configurations
        conf1 = self.dbsession.query(Configuration).filter_by(id=1).all()
        assert [] == conf1

    # Such method no longer exists. Either remove the test or create such method.
    def test_getConfsForExperimentgroup(self):
        configurations = ExperimentGroup.get(1).configurations
        conf1 = self.dbsession.query(Configuration).filter_by(id=1).one()
        conf2 = self.dbsession.query(Configuration).filter_by(id=2).one()

        assert configurations == [conf1, conf2]

    # Such method no longer exists. Either remove the test or create such method.
    def test_getTotalConfigurationForUser(self):
        current_groups = User.get(1).experimentgroups
        configurations = list(map(lambda _: _.configurations, current_groups))
        conf1 = Configuration.get(1)
        conf2 = Configuration.get(2)

        assert configurations == [[conf1, conf2]]
