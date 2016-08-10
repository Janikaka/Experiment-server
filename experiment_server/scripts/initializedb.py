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
from ..models import (Experiment, User, DataItem, ExperimentGroup, Configuration)

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

        user1 = User(username='First user')
        user2 = User(username='Second user')
        user3 = User(username='Third user')
        dbsession.add(user1)
        dbsession.add(user2)
        dbsession.add(user3)

        dataitem1 = DataItem(
            key='key1',
            value=10,
            startDatetime=datetime.datetime(
                dateTimeNow.year-1, 
                dateTimeNow.month, 
                dateTimeNow.day,
                dateTimeNow.hour,
                dateTimeNow.minute,
                dateTimeNow.second+1),
            endDatetime=datetime.datetime(
                dateTimeNow.year-1, 
                dateTimeNow.month, 
                dateTimeNow.day,
                dateTimeNow.hour+1,
                dateTimeNow.minute,
                dateTimeNow.second)
            )
        dataitem2 = DataItem(
            key='key2',
            value=20,
            startDatetime=datetime.datetime(
                dateTimeNow.year-1, 
                dateTimeNow.month, 
                dateTimeNow.day,
                dateTimeNow.hour+2,
                dateTimeNow.minute,
                dateTimeNow.second),
            endDatetime=datetime.datetime(
                dateTimeNow.year-1, 
                dateTimeNow.month, 
                dateTimeNow.day,
                dateTimeNow.hour+3,
                dateTimeNow.minute,
                dateTimeNow.second)
            )
        dataitem3 = DataItem(
            key='key3',
            value=30,
            startDatetime=datetime.datetime(
                dateTimeNow.year, 
                dateTimeNow.month, 
                dateTimeNow.day,
                dateTimeNow.hour,
                dateTimeNow.minute,
                dateTimeNow.second+1),
            endDatetime=datetime.datetime(
                dateTimeNow.year, 
                dateTimeNow.month, 
                dateTimeNow.day,
                dateTimeNow.hour+1,
                dateTimeNow.minute,
                dateTimeNow.second)
            )
        dataitem4 = DataItem(
            key='key4',
            value=40,
            startDatetime=datetime.datetime(
                dateTimeNow.year, 
                dateTimeNow.month, 
                dateTimeNow.day,
                dateTimeNow.hour+2,
                dateTimeNow.minute,
                dateTimeNow.second),
            endDatetime=datetime.datetime(
                dateTimeNow.year, 
                dateTimeNow.month, 
                dateTimeNow.day,
                dateTimeNow.hour+3,
                dateTimeNow.minute,
                dateTimeNow.second)
            )
        dataitem5 = DataItem(
            key='key5',
            value=50,
            startDatetime=datetime.datetime(
                dateTimeNow.year+1, 
                dateTimeNow.month, 
                dateTimeNow.day,
                dateTimeNow.hour,
                dateTimeNow.minute,
                dateTimeNow.second+1),
            endDatetime=datetime.datetime(
                dateTimeNow.year+1, 
                dateTimeNow.month, 
                dateTimeNow.day,
                dateTimeNow.hour+1,
                dateTimeNow.minute,
                dateTimeNow.second)
            )
        dataitem6 = DataItem(
            key='key6',
            value=60,
            startDatetime=datetime.datetime(
                dateTimeNow.year+1, 
                dateTimeNow.month, 
                dateTimeNow.day,
                dateTimeNow.hour+2,
                dateTimeNow.minute,
                dateTimeNow.second),
            endDatetime=datetime.datetime(
                dateTimeNow.year+1, 
                dateTimeNow.month, 
                dateTimeNow.day,
                dateTimeNow.hour+3,
                dateTimeNow.minute,
                dateTimeNow.second)
            )

        dbsession.add(dataitem1)
        dbsession.add(dataitem2)
        dbsession.add(dataitem3)
        dbsession.add(dataitem4)
        dbsession.add(dataitem5)
        dbsession.add(dataitem6)

        user2.dataitems.append(dataitem1)
        user2.dataitems.append(dataitem2)
        user1.dataitems.append(dataitem3)
        user2.dataitems.append(dataitem4)
        user3.dataitems.append(dataitem5)
        user3.dataitems.append(dataitem6)

        experiment1 = Experiment(name='Running experiment', 
            startDatetime=dateTimeNow, 
            endDatetime=datetime.datetime(
                dateTimeNow.year+1, 
                dateTimeNow.month, 
                dateTimeNow.day,
                dateTimeNow.hour,
                dateTimeNow.minute,
                dateTimeNow.second),
            size=100)
        experiment2 = Experiment(name='Finished experiment', 
            startDatetime=datetime.datetime(
                dateTimeNow.year-1, 
                dateTimeNow.month, 
                dateTimeNow.day,
                dateTimeNow.hour,
                dateTimeNow.minute,
                dateTimeNow.second),
            endDatetime=dateTimeNow,
            size=100)
        experiment3 = Experiment(name='Waiting experiment', 
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

        experimentgroup1A = ExperimentGroup(name='group 1 A', users=[user1])
        experimentgroup1B = ExperimentGroup(name='group 1 B', users=[user2])

        experimentgroup2A = ExperimentGroup(name='group 2 A', users=[user2])
        experimentgroup2B = ExperimentGroup(name='group 2 B', users=[])

        experimentgroup3A = ExperimentGroup(name='group 3 A', users=[user3])
        experimentgroup3B = ExperimentGroup(name='group 3 B', users=[])

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

        conf1 = Configuration(key='level', value=2, experimentgroup=experimentgroup1A)
        conf2 = Configuration(key='operators', value=0, experimentgroup=experimentgroup1A)
        conf3 = Configuration(key='howTo', value=True, experimentgroup=experimentgroup1A)
        conf4 = Configuration(key='highScore', value= True, experimentgroup=experimentgroup1A)
        conf5 = Configuration(key='skip', value=1, experimentgroup=experimentgroup1A)

        conf6 = Configuration(key='level', value=3, experimentgroup=experimentgroup1B)
        conf7 = Configuration(key='operators', value=2, experimentgroup=experimentgroup1B)
        conf8 = Configuration(key='howTo', value=False, experimentgroup=experimentgroup1B)
        conf9 = Configuration(key='highScore', value=False, experimentgroup=experimentgroup1B)
        conf10 = Configuration(key='skip', value=2, experimentgroup=experimentgroup1B)
        
        
        dbsession.add(conf1)
        dbsession.add(conf2)
        dbsession.add(conf3)
        dbsession.add(conf4)
        dbsession.add(conf5)
        dbsession.add(conf6)
        dbsession.add(conf7)
        dbsession.add(conf8)
        dbsession.add(conf9)
        dbsession.add(conf10)
