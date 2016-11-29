import datetime
from .base_test import BaseTest
from ..models import (Experiment, Client, ExperimentGroup, Configuration)


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
        clientsFromDB = self.dbsession.query(Client).all()
        Configuration.save(Configuration(id=23, key='v1', value=1.0))
        expgroup_count_before = ExperimentGroup.query().count()

        expgroup = ExperimentGroup(name="These tests are horrible",
            experiment=Experiment.get(1),
            configurations=[Configuration.get(23)])

        ExperimentGroup.save(expgroup)
        expgroup_count_now = ExperimentGroup.query().count()

        assert expgroup_count_now > expgroup_count_before
        assert ExperimentGroup.get_by('name', 'These tests are horrible') is not None

    def test_deleteExperimentgroup(self):
        expgroup_count_before = ExperimentGroup.query().count()
        ExperimentGroup.destroy(ExperimentGroup.get(1))

        expgroup_count_after = ExperimentGroup.query().count()
        experimentgroups = [self.dbsession.query(ExperimentGroup).filter_by(id=2).one()]
        configurations = [self.dbsession.query(Configuration).filter_by(id=3).one(),
                          self.dbsession.query(Configuration).filter_by(id=4).one()]

        assert expgroup_count_after < expgroup_count_before

    def test_deleteExperimentgroup_clients_reference_is_deleted(self):
        ExperimentGroup.destroy(ExperimentGroup.get(1))

        clientsFromDB = self.dbsession.query(Client)\
            .join(Client.experimentgroups).filter(ExperimentGroup.id == 1).all()

        assert clientsFromDB == []

    def test_deleteExperimentgroup_configurations_are_deleted(self):
        ExperimentGroup.destroy(ExperimentGroup.get(1))

        configurationsFromDB = self.dbsession.query(Configuration)\
            .filter(Configuration.experimentgroup_id == 1).all()

        assert configurationsFromDB == []

    def test_getExperimentgroupForclientInExperiment(self):
        expgroupInExperimentForclient1 = self.DB.get_experimentgroup_for_client_in_experiment(1, 1)
        expgroupInExperimentForclient2 = self.DB.get_experimentgroup_for_client_in_experiment(2, 1)

        expgroup1 = self.dbsession.query(ExperimentGroup).filter_by(id=1).one()
        expgroup2 = self.dbsession.query(ExperimentGroup).filter_by(id=2).one()

        assert expgroupInExperimentForclient1 == expgroup1
        assert expgroupInExperimentForclient2 == expgroup2
