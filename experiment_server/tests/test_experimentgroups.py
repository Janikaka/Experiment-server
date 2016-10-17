import datetime
from .base_test import BaseTest
from ..models import (Experiment, User, ExperimentGroup, Configuration)


def strToDatetime(date):
    return datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

# ---------------------------------------------------------------------------------
#                                DatabaseInterface
# ---------------------------------------------------------------------------------

class TestExperimentGroups(BaseTest):
    def setUp(self):
        super(TestExperimentGroups, self).setUp()
        self.init_database()
        self.init_databaseData()

    def test_createExperimentgroup(self):
        expgroupsFromDB = self.dbsession.query(ExperimentGroup).all()
        experimentsFromDB = self.dbsession.query(Experiment).all()
        configurationsFromDB = self.dbsession.query(Configuration).all()
        usersFromDB = self.dbsession.query(User).all()

        expgroup1 = {
            'id': 1,
            'name': 'Group A',
            'experiment': experimentsFromDB[0],
            'configurations': [configurationsFromDB[0], configurationsFromDB[1]],
            'users': [usersFromDB[0]]
        }
        expgroup2 = {
            'id': 2,
            'name': 'Group B',
            'experiment': experimentsFromDB[0],
            'configurations': [configurationsFromDB[2], configurationsFromDB[3]],
            'users': [usersFromDB[1]]
        }
        expgroups = [expgroup1, expgroup2]

        for i in range(len(expgroupsFromDB)):
            for key in expgroups[i]:
                assert getattr(expgroupsFromDB[i], key) == expgroups[i][key]

    def test_deleteExperimentgroup(self):
        self.DB.delete_experimentgroup(1)

        expgroupsFromDB = self.dbsession.query(ExperimentGroup).all()
        experimentsFromDB = self.dbsession.query(Experiment).all()
        configurationsFromDB = self.dbsession.query(Configuration).all()
        usersFromDB = self.dbsession.query(User).all()

        experimentgroups = [self.dbsession.query(ExperimentGroup).filter_by(id=2).one()]
        configurations = [self.dbsession.query(Configuration).filter_by(id=3).one(),
                          self.dbsession.query(Configuration).filter_by(id=4).one()]

        assert expgroupsFromDB == experimentgroups
        assert experimentsFromDB[0].experimentgroups == experimentgroups
        assert configurationsFromDB == configurations
        assert usersFromDB[0].experimentgroups == []
        assert usersFromDB[1].experimentgroups == experimentgroups

    def test_getExperimentgroupForUserInExperiment(self):
        expgroupInExperimentForUser1 = self.DB.get_experimentgroup_for_user_in_experiment(1, 1)
        expgroupInExperimentForUser2 = self.DB.get_experimentgroup_for_user_in_experiment(2, 1)

        expgroup1 = self.dbsession.query(ExperimentGroup).filter_by(id=1).one()
        expgroup2 = self.dbsession.query(ExperimentGroup).filter_by(id=2).one()

        assert expgroupInExperimentForUser1 == expgroup1
        assert expgroupInExperimentForUser2 == expgroup2
