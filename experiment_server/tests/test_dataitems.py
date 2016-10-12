import datetime
from .base_test import BaseTest
from ..models import (Experiment, User, DataItem)


def strToDatetime(date):
    return datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

# ---------------------------------------------------------------------------------
#                                DatabaseInterface
# ---------------------------------------------------------------------------------

class TestDataitems(BaseTest):
    def setUp(self):
        super(TestDataitems, self).setUp()
        self.init_database()
        self.init_databaseData()

    def test_createDataitem(self):
        dataitemsFromDB = self.dbsession.query(DataItem).all()
        user1 = self.dbsession.query(User).filter_by(id=1).one()
        user2 = self.dbsession.query(User).filter_by(id=2).one()
        dt1 = {'key': 'key1',
               'value': 10,
               'startDatetime': strToDatetime('2016-01-01 00:00:00'),
               'endDatetime': strToDatetime('2016-01-01 01:01:01'),
               'user': user1}
        dt2 = {'key': 'key2',
               'value': 0.5,
               'startDatetime': strToDatetime('2016-02-02 01:01:02'),
               'endDatetime': strToDatetime('2016-02-02 02:02:02'),
               'user': user1}
        dt3 = {'key': 'key3',
               'value': 'liked',
               'startDatetime': strToDatetime('2016-03-03 00:00:00'),
               'endDatetime': strToDatetime('2016-03-03 03:03:03'),
               'user': user2}
        dt4 = {'key': 'key4',
               'value': False,
               'startDatetime': strToDatetime('2016-04-04 03:03:04'),
               'endDatetime': strToDatetime('2016-04-04 04:04:04'),
               'user': user2}
        dataitems = [dt1, dt2, dt3, dt4]

        for i in range(len(dataitemsFromDB)):
            for key in dataitems[i]:
                assert getattr(dataitemsFromDB[i], key) == dataitems[i][key]

    def test_getTotalDataitemsForExperiment(self):
        totalDataitemsForExperiment = self.DB.get_total_dataitems_for_experiment(1)

        assert totalDataitemsForExperiment == 4

    def test_getTotalDataitemsForExpgroup(self):
        totalDataitemsForExpgroup1 = self.DB.get_total_dataitems_for_expgroup(1)
        totalDataitemsForExpgroup2 = self.DB.get_total_dataitems_for_expgroup(2)

        assert totalDataitemsForExpgroup1 == 2
        assert totalDataitemsForExpgroup2 == 2

    def test_getTotalDataitemsForUserInExperiment(self):
        totalDataitemsForUser1InExperiment = self.DB.get_total_dataitems_for_user_in_experiment(1, 1)
        totalDataitemsForUser2InExperiment = self.DB.get_total_dataitems_for_user_in_experiment(2, 1)

        assert totalDataitemsForUser1InExperiment == 2
        assert totalDataitemsForUser2InExperiment == 2

    def test_getDataitemsForUserOnPeriod(self):
        user1 = self.dbsession.query(User).filter_by(id=1).one()
        dt1 = self.dbsession.query(DataItem).filter_by(id=1).one()
        startDatetime = strToDatetime('2016-01-01 00:00:00')
        endDatetime = strToDatetime('2016-01-01 02:01:01')
        dataitems = self.DB.get_dataitems_for_user_on_period(user1.id, startDatetime, endDatetime)

        assert dataitems == [dt1]

    def test_getDataitemsForUserInExperiment(self):
        user1 = self.dbsession.query(User).filter_by(id=1).one()
        dt1 = self.dbsession.query(DataItem).filter_by(id=1).one()
        dt2 = self.dbsession.query(DataItem).filter_by(id=2).one()
        dataitems = self.DB.get_dataitems_for_user_in_experiment(1, 1)

        assert dataitems == [dt1, dt2]

    def test_getDataitemsForExperimentgroup(self):
        dt1 = self.dbsession.query(DataItem).filter_by(id=1).one()
        dt2 = self.dbsession.query(DataItem).filter_by(id=2).one()
        dataitems = self.DB.get_dataitems_for_experimentgroup(1)

        assert dataitems == [dt1, dt2]

    def test_getDataitemsForExperiment(self):
        dt1 = self.dbsession.query(DataItem).filter_by(id=1).one()
        dt2 = self.dbsession.query(DataItem).filter_by(id=2).one()
        dt3 = self.dbsession.query(DataItem).filter_by(id=3).one()
        dt4 = self.dbsession.query(DataItem).filter_by(id=4).one()
        dataitems = self.DB.get_dataitems_for_experiment(1)

        assert dataitems == [dt1, dt2, dt3, dt4]

    def test_deleteDataitem(self):
        dt1 = self.dbsession.query(DataItem).filter_by(id=1).one()
        user1 = self.dbsession.query(User).filter_by(id=1).one()
        assert dt1 in user1.dataitems
        self.DB.delete_dataitem(dt1.id)
        assert dt1 not in user1.dataitems
        dt1 = self.dbsession.query(DataItem).filter_by(id=1).all()
        assert [] == dt1
