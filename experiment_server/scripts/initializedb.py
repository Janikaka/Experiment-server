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

        user1 = User(username='First user')
        user2 = User(username='Second user')
        
        dataitem1 = DataItem(
            key='key1',
            value=10,
            startDatetime=datetime.datetime.now(),
            endDatetime=datetime.datetime.now()
            )
        dataitem2 = DataItem(
            key='key2',
            value=20,
            startDatetime=datetime.datetime.now(),
            endDatetime=datetime.datetime.now()
            )

        user1.dataitems.append(dataitem1)
        user2.dataitems.append(dataitem2)

        dt = datetime.datetime.now()
        dateTimeNow = datetime.datetime(
                dt.year, 
                dt.month, 
                dt.day,
                dt.hour,
                dt.minute,
                dt.second)
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
            startDatetime=dateTimeNow, 
            endDatetime=datetime.datetime(
                dateTimeNow.year, 
                dateTimeNow.month, 
                dateTimeNow.day,
                dateTimeNow.hour,
                dateTimeNow.minute,
                dateTimeNow.second+1),
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


        experimentgroup1 = ExperimentGroup(name='group A', users=[user1])
        experimentgroup2 = ExperimentGroup(name='group B', users=[user2])

        experiment1.experimentgroups.append(experimentgroup1)
        experiment1.experimentgroups.append(experimentgroup2)

        conf1 = Configuration(key='v1', value= 3, experimentgroup=experimentgroup1)
        conf2 = Configuration(key='v2', value= 0.2, experimentgroup=experimentgroup1)
        conf3 = Configuration(key='v3', value= 'hard', experimentgroup=experimentgroup1)
        conf4 = Configuration(key='v4', value= True, experimentgroup=experimentgroup1)

        conf5 = Configuration(key='v1', value= 2, experimentgroup=experimentgroup2)
        conf6 = Configuration(key='v2', value= 0.3, experimentgroup=experimentgroup2)
        conf7 = Configuration(key='v3', value= 'easy', experimentgroup=experimentgroup2)
        conf8 = Configuration(key='v4', value= False, experimentgroup=experimentgroup2)

        dbsession.add(dataitem1)
        dbsession.add(dataitem2)
        dbsession.add(user1)
        dbsession.add(user2)
        dbsession.add(experimentgroup1)
        dbsession.add(experimentgroup2)
        dbsession.add(experiment1)
        dbsession.add(experiment2)
        dbsession.add(experiment3)
        dbsession.add(conf1)
        dbsession.add(conf2)
        dbsession.add(conf3)
        dbsession.add(conf4)
        dbsession.add(conf5)
        dbsession.add(conf6)
        dbsession.add(conf7)
        dbsession.add(conf8)
