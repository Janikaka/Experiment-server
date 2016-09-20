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
from ..models import (Experiment, User, DataItem, ExperimentGroup, Configuration, Application)

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

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

        experiment1 = Experiment(name='High score', 
            startDatetime=dateTimeNow, 
            endDatetime=datetime.datetime(
                dateTimeNow.year+1, 
                dateTimeNow.month, 
                dateTimeNow.day,
                dateTimeNow.hour,
                dateTimeNow.minute,
                dateTimeNow.second),
            size=100)
        experiment2 = Experiment(name='Game level', 
            startDatetime=datetime.datetime(
                dateTimeNow.year-1, 
                dateTimeNow.month, 
                dateTimeNow.day,
                dateTimeNow.hour,
                dateTimeNow.minute,
                dateTimeNow.second),
            endDatetime=dateTimeNow,
            size=100)
        experiment3 = Experiment(name='Operators', 
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
                dateTimeNow.second),
            size=100)

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

        app1 = Application(name='Math Game')

        dbsession.add(app1)
