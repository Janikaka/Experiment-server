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
from ..models import (Experiments, Users, DataItems, ExperimentGroups, Configurations)



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

        user1 = Users(username='First user', password='First password')
        user2 = Users(username='Second user')
        
        dataitem1 = DataItems(value=10)
        dataitem2 = DataItems(value=20)

        user1.dataitems.append(dataitem1)
        user2.dataitems.append(dataitem2)

        experiment1 = Experiments(name='First experiment')


        experimentgroup1 = ExperimentGroups(name='group A', users=[user1])
        experimentgroup2 = ExperimentGroups(name='group B', users=[user2])

        experiment1.experimentgroups.append(experimentgroup1)
        experiment1.experimentgroups.append(experimentgroup2)

        conf1 = Configurations(key='confkey1', value=1, experimentgroup=experimentgroup1)
        conf2 = Configurations(key='confkey2', value=2, experimentgroup=experimentgroup2)


        dbsession.add(dataitem1)
        dbsession.add(dataitem2)
        dbsession.add(user1)
        dbsession.add(user2)
        dbsession.add(experimentgroup1)
        dbsession.add(experimentgroup2)
        dbsession.add(experiment1)
        dbsession.add(conf1)
        dbsession.add(conf2)








