import os
import sys
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models.meta import Base
from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )
from ..models import (Experiment, Client, DataItem, ExperimentGroup, Configuration,
                      Application, ConfigurationKey, Operator, RangeConstraint, ExclusionConstraint)

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

# Performs database setup. Initialization creates required tables, and some test
# data. When called, the first parameter is the configuration-file's name. When
# done at production enviroment, please give database's URL.
# Params:   argv[1]: configuration file
#           argv[2 + n]: optional variables. Can set configuration variables.
def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        import datetime

        dt = datetime.datetime.now()
        dateTimeNow = datetime.datetime(
                dt.year,
                dt.month,
                dt.day,
                dt.hour,
                dt.minute,
                dt.second)

        import uuid
        app1 = Application(name='Math Game', apikey=str(uuid.uuid4()))

        dbsession.add(app1)

        experiment1 = Experiment(
            name='High score',
            application=app1,
            startDatetime=dateTimeNow,
            endDatetime=datetime.datetime(
                dateTimeNow.year+1,
                dateTimeNow.month,
                dateTimeNow.day,
                dateTimeNow.hour,
                dateTimeNow.minute,
                dateTimeNow.second))
        experiment2 = Experiment(
            name='Game level',
            application=app1,
            startDatetime=datetime.datetime(
                dateTimeNow.year-1,
                dateTimeNow.month,
                dateTimeNow.day,
                dateTimeNow.hour,
                dateTimeNow.minute,
                dateTimeNow.second),
            endDatetime=dateTimeNow)
        experiment3 = Experiment(
            name='Operators',
            application=app1,
            startDatetime=datetime.datetime(
                dateTimeNow.year+1,
                dateTimeNow.month,
                dateTimeNow.day,
                dateTimeNow.hour,
                dateTimeNow.minute,
                dateTimeNow.second),
            endDatetime=datetime.datetime(
                dateTimeNow.year+2,
                dateTimeNow.month,
                dateTimeNow.day,
                dateTimeNow.hour,
                dateTimeNow.minute,
                dateTimeNow.second))

        dbsession.add(experiment1)
        dbsession.add(experiment2)
        dbsession.add(experiment3)

        experimentgroup1A = ExperimentGroup(name='High score ON')
        experimentgroup1B = ExperimentGroup(name='High score OFF')

        experimentgroup2A = ExperimentGroup(name='Level 1')
        experimentgroup2B = ExperimentGroup(name='Level 5')

        experimentgroup3A = ExperimentGroup(name='Add/Subtract')
        experimentgroup3B = ExperimentGroup(name='Multiply/Divide')

        dbsession.add(experimentgroup1A)
        dbsession.add(experimentgroup1B)
        dbsession.add(experimentgroup2A)
        dbsession.add(experimentgroup2B)
        dbsession.add(experimentgroup3A)
        dbsession.add(experimentgroup3B)

        experiment1.experimentgroups.append(experimentgroup1A)
        experiment1.experimentgroups.append(experimentgroup1B)
        experiment2.experimentgroups.append(experimentgroup2A)
        experiment2.experimentgroups.append(experimentgroup2B)
        experiment3.experimentgroups.append(experimentgroup3A)
        experiment3.experimentgroups.append(experimentgroup3B)

        conf1 = Configuration(key='highScore', value=True, experimentgroup=experimentgroup1A)
        conf2 = Configuration(key='highScore', value=False, experimentgroup=experimentgroup1B)

        conf3 = Configuration(key='level', value=1, experimentgroup=experimentgroup2A)
        conf4 = Configuration(key='level', value=5, experimentgroup=experimentgroup2B)

        conf5 = Configuration(key='operators', value=0, experimentgroup=experimentgroup3A)
        conf6 = Configuration(key='operators', value=1, experimentgroup=experimentgroup3A)
        conf7 = Configuration(key='operators', value=2, experimentgroup=experimentgroup3B)
        conf8 = Configuration(key='operators', value=3, experimentgroup=experimentgroup3B)

        dbsession.add(conf1)
        dbsession.add(conf2)
        dbsession.add(conf3)
        dbsession.add(conf4)
        dbsession.add(conf5)
        dbsession.add(conf6)
        dbsession.add(conf7)
        dbsession.add(conf8)

        confk1 = ConfigurationKey(application=app1, name='highscore', type='boolean')
        confk2 = ConfigurationKey(application=app1, name='difficulty', type='integer')
        confk3 = ConfigurationKey(application=app1, name='speed', type='double')

        dbsession.add(confk1)
        dbsession.add(confk2)
        dbsession.add(confk3)

        op1 = Operator(math_value='=', human_value='equals')
        op2 = Operator(math_value='<=', human_value='less or equal than')
        op3 = Operator(math_value='<', human_value='less than')
        op4 = Operator(math_value='>=', human_value='greater or equal than')
        op5 = Operator(math_value='>', human_value='greater than')
        op6 = Operator(math_value='!=', human_value='not equal')
        op7 = Operator(math_value='[]', human_value='inclusive')
        op8 = Operator(math_value='()', human_value='exclusive')
        op9 = Operator(math_value='def', human_value='must define')
        op10 = Operator(math_value='ndef', human_value='must not define')

        dbsession.add(op1)
        dbsession.add(op2)
        dbsession.add(op3)
        dbsession.add(op4)
        dbsession.add(op5)
        dbsession.add(op6)
        dbsession.add(op7)
        dbsession.add(op8)
        dbsession.add(op9)
        dbsession.add(op10)

        us1 =Client(clientname='Julio')

        dbsession.add(us1)

        rc1 = RangeConstraint(configurationkey=confk2, operator=op4, value="1")
        rc2 = RangeConstraint(configurationkey=confk2, operator=op2, value="5")
        rc3 = RangeConstraint(configurationkey=confk3, operator=op5, value="0")

        dbsession.add(rc1)
        dbsession.add(rc2)
        dbsession.add(rc3)

        exc1 = ExclusionConstraint(first_configurationkey=confk1, first_operator=op9,
                                   first_value_a=None, first_value_b=None,
                                   second_configurationkey=confk2, second_operator=None,
                                   second_value_a=None, second_value_b=None)
        exc2 = ExclusionConstraint(first_configurationkey=confk1, first_operator=op9,
                                   first_value_a=None, first_value_b=None,
                                   second_configurationkey=confk2, second_operator=op4,
                                   second_value_a="2", second_value_b=None)

        dbsession.add(exc1)
        dbsession.add(exc2)
