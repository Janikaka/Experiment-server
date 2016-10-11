from ..models import (Experiment, User, DataItem, ExperimentGroup, Configuration,
                      Application, ConfigurationKey, Operator, RangeConstraint, ExclusionConstraint)


class DatabaseData:
    def create_database(self):

        app1 = Application(name='App 1')
        Application.save(app1)

        app2 = Application(name='App 2')
        Application.save(app2)

        confk1 = ConfigurationKey(application=app1, name='highscore', type='boolean')
        ConfigurationKey.save(confk1)

        confk2 = ConfigurationKey(application=app1, name='difficulty', type='integer')
        ConfigurationKey.save(confk2)

