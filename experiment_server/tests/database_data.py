from ..models import (Experiment, User, DataItem, DatabaseInterface, ExperimentGroup, Configuration,
                      Application, ConfigurationKey, Operator, RangeConstraint, ExclusionConstraint)


class DatabaseData:
    def create_database(self):

        self.DB = DatabaseInterface(self.dbsession)

        app1 = Application(name='App 1')
        Application.save(app1)

        confk1 = ConfigurationKey(application=app1, name='highscore', type='boolean')
        ConfigurationKey.save(confk1)

        confk2 = ConfigurationKey(application=app1, name='difficulty', type='integer')
        ConfigurationKey.save(confk2)

        op1 = Operator(math_value='<=', human_value='less or equal than')
        Operator.save(op1)

        op2 = Operator(math_value='>=', human_value='greater or equal than')
        Operator.save(op2)

        op3 = Operator(math_value='def', human_value='must define')
        Operator.save(op3)

        rc1 = RangeConstraint(configurationkey=confk2, operator=op2, value=1)
        RangeConstraint.save(rc1)

        rc2 = RangeConstraint(configurationkey=confk2, operator=op1, value=5)
        RangeConstraint.save(rc2)

        exc1 = ExclusionConstraint(first_configurationkey=confk1, first_operator=op3,
                                   first_value_a=None, first_value_b=None,
                                   second_configurationkey=confk2, second_operator=None,
                                   second_value_a=None, second_value_b=None)
        ExclusionConstraint.save(exc1)

        app2 = Application(name='App 2')
        Application.save(app2)

        expgroup1 = self.DB.create_experimentgroup(
            {'name': 'Group A'
             })
        expgroup2 = self.DB.create_experimentgroup(
            {'name': 'Group B'
             })

        conf1 = self.DB.create_configuration(
            {'key': 'v1',
             'value': 0.5,
             'experimentgroup': expgroup1
             })
        conf2 = self.DB.create_configuration(
            {'key': 'v2',
             'value': True,
             'experimentgroup': expgroup1
             })
        conf3 = self.DB.create_configuration(
            {'key': 'v1',
             'value': 1.0,
             'experimentgroup': expgroup2
             })
        conf4 = self.DB.create_configuration(
            {'key': 'v2',
             'value': False,
             'experimentgroup': expgroup2
             })

        experiment = self.DB.create_experiment(
            {'name': 'Test experiment',
             'application': app1,
             'startDatetime': '2016-01-01 00:00:00',
             'endDatetime': '2017-01-01 00:00:00',
             'size': 100,
             'experimentgroups': [expgroup1, expgroup2]
             })

        user1 = self.DB.create_user(
            {'username': 'First user',
             'experimentgroups': [expgroup1]
             })
        user2 = self.DB.create_user(
            {'username': 'Second user',
             'experimentgroups': [expgroup2]
             })

        dt1 = self.DB.create_dataitem(
            {'key': 'key1',
             'value': 10,
             'startDatetime': '2016-01-01 00:00:00',
             'endDatetime': '2016-01-01 01:01:01',
             'user': user1
             })
        dt2 = self.DB.create_dataitem(
            {'key': 'key2',
             'value': 0.5,
             'startDatetime': '2016-02-02 01:01:02',
             'endDatetime': '2016-02-02 02:02:02',
             'user': user1
             })
        dt3 = self.DB.create_dataitem(
            {'key': 'key3',
             'value': 'liked',
             'startDatetime': '2016-03-03 00:00:00',
             'endDatetime': '2016-03-03 03:03:03',
             'user': user2
             })
        dt4 = self.DB.create_dataitem(
            {'key': 'key4',
             'value': False,
             'startDatetime': '2016-04-04 03:03:04',
             'endDatetime': '2016-04-04 04:04:04',
             'user': user2
             })