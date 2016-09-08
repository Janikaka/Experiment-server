""" import modules """
from .experimentgroups import ExperimentGroup
from .experiments import Experiment
from .users import User
from .dataitems import DataItem
from .configurations import Configuration
import random
import datetime
from sqlalchemy import and_
from sqlalchemy import func


class DatabaseInterface(object): # this is New-style class naming rule
    """This interface is used for creating data for database and getting data from database"""
    def __init__(self, dbsession):
        self.dbsession = dbsession

    # ---------------------------------------------------------------------------------
    #                                   Experiments
    # ---------------------------------------------------------------------------------
    def create_experiment(self, data):
        """create experiment"""
        name = data['name']
        experimentgroups = data['experimentgroups']
        start_datetime = datetime.datetime.strptime(data['startDatetime'], "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.datetime.strptime(data['endDatetime'], "%Y-%m-%d %H:%M:%S")
        size = data['size']
        experiment = Experiment(
            name=name,
            startDatetime=start_datetime,
            endDatetime=end_datetime,
            size=size,
            experimentgroups=experimentgroups)
        self.dbsession.add(experiment)
        return self.dbsession.query(Experiment).filter(
            Experiment.id == self.dbsession.query(func.max(Experiment.id))).first()

    def delete_experiment(self, id):
        experiment = self.dbsession.query(Experiment).filter_by(id=id).first()
        if experiment is None:
            return False
        experimentgroups = experiment.experimentgroups
        for experimentgroup in experimentgroups:
            self.delete_experimentgroup_in_users(experimentgroup.id)
        self.dbsession.delete(experiment)
        return [] == self.dbsession.query(Experiment).filter_by(id=id).all()

    def get_all_experiments(self):
        return self.dbsession.query(Experiment).all()

    def get_status_for_experiment(self, id):
        # open = 'open'
        running = 'running'
        finished = 'finished'
        waiting = 'waiting'

        experiment = self.get_experiment(id)
        date_time_now = datetime.datetime.now()
        start_datetime = experiment.startDatetime
        end_datetime = experiment.endDatetime
        if start_datetime >= end_datetime:
            # validate this earlier
            return None
        if start_datetime <= date_time_now and date_time_now <= end_datetime:
            return running
        elif date_time_now > end_datetime:
            return finished
        elif date_time_now < start_datetime:
            return waiting
        return None

    def get_experiment(self, id):
        return self.dbsession.query(Experiment).filter_by(id=id).first()

    def get_all_running_experiments(self):
        dateTimeNow = datetime.datetime.now()
        return self.dbsession.query(Experiment).filter(
            and_(Experiment.startDatetime <= dateTimeNow,
                 dateTimeNow <= Experiment.endDatetime)).all()

    def get_experiments_user_participates(self, id):
        experimentgroups = self.get_experimentgroups_for_user(id)
        experiments = []
        for experimentgroup in experimentgroups:
            experiments.append(experimentgroup.experiment)
        return experiments

    # ---------------------------------------------------------------------------------
    #                                 ExperimentGroups
    # ---------------------------------------------------------------------------------

    def create_experimentgroup(self, data):
        name = data['name']
        experimentgroup = ExperimentGroup(name=name)
        self.dbsession.add(experimentgroup)
        return self.dbsession.query(ExperimentGroup).order_by(ExperimentGroup.id.desc()).first()

    def delete_experimentgroup(self, id):
        experimentgroup = self.dbsession.query(ExperimentGroup).filter_by(id=id).first()
        if experimentgroup is None:
            return False
        self.delete_experimentgroup_in_users(id)
        experimentgroup.experiment.experimentgroups.remove(experimentgroup)
        self.dbsession.delete(experimentgroup)
        return [] == self.dbsession.query(ExperimentGroup).filter_by(id=id).all()

    def delete_experimentgroup_in_users(self, experimentgroup_id):
        experimentgroup = self.get_experimentgroup(experimentgroup_id)
        if experimentgroup is None:
            return False
        for user in experimentgroup.users:
            user.experimentgroups.remove(experimentgroup)

    def get_experimentgroup(self, id):
        return self.dbsession.query(ExperimentGroup).filter_by(id=id).first()

    def get_experimentgroups(self, id):
        return self.dbsession.query(ExperimentGroup).filter_by(experiment_id=id).all()

    def get_experimentgroup_for_user_in_experiment(self, userId, experimentId):
        expgroups = self.get_experimentgroups_for_user(userId)
        if expgroups is None:
            return None
        for expgroup in expgroups:
            if expgroup.experiment_id == experimentId:
                return expgroup

    def get_experimentgroups_for_user(self, id):
        user = self.dbsession.query(User).filter_by(id=id).first()
        if user is None:
            return None
        return user.experimentgroups

    # ---------------------------------------------------------------------------------
    #                                      Users
    # ---------------------------------------------------------------------------------

    def create_user(self, data):
        keys = ['username', 'password', 'experimentgroups', 'dataitems']
        for key in keys:
            try:
                data[key]
            except KeyError:
                data[key] = []
        user = User(username=data['username'],
                    experimentgroups=data['experimentgroups'],
                    dataitems=data['dataitems'])
        self.dbsession.add(user)
        return self.dbsession.query(User).order_by(User.id.desc()).first()

    def get_user_by_id(self, id):
        return self.dbsession.query(User).filter_by(id=id).first()

    def get_user_by_username(self, username):
        return self.dbsession.query(User).filter_by(username=username).first()

    def get_all_users(self):
        return self.dbsession.query(User).all()

    def delete_user(self, id):
        user = self.dbsession.query(User).filter_by(id=id).first()
        if user is None:
            return False
        for experimentgroup in user.experimentgroups:
            experimentgroup.users.remove(user)
        self.dbsession.delete(user)
        return [] == self.dbsession.query(User).filter_by(id=id).all()

    def get_user(self, username):
        user = self.dbsession.query(User).filter_by(username=username).all()
        if user == []:
            return self.create_user({'username': username})
        else:
            return user[0]

    def assign_user_to_experiment(self, user_id, experiment_id):
        experimentgroups = self.get_experimentgroups(experiment_id)
        if len(experimentgroups) == 1:
            experimentgroup = experimentgroups[0]
        else:
            experimentgroup = experimentgroups[random.randint(0, len(experimentgroups) - 1)]
        self.dbsession.query(User)\
            .filter_by(id=user_id).first()\
            .experimentgroups.append(experimentgroup)

    def assign_user_to_experiments(self, id):
        # We are (now) assigning users only for running experiments
        allExperiments = self.get_all_running_experiments()
        experimentsUserParticipates = self.get_experiments_user_participates(id)
        experimentsUserDoesNotParticipate = []
        for experiment in allExperiments:
            if experiment not in experimentsUserParticipates:
                experimentsUserDoesNotParticipate.append(experiment)
        experimentsUserShouldParticipate = experimentsUserDoesNotParticipate
        for experiment in experimentsUserShouldParticipate:
            self.assign_user_to_experiment(id, experiment.id)

    def get_users_for_experiment(self, id):
        experiment = self.get_experiment(id)
        if experiment is None:
            return None
        users = []
        for experimentgroup in experiment.experimentgroups:
            users.extend(experimentgroup.users)
        return users

    def delete_user_from_experiment(self, userId, experimentId):
        expgroup = self.get_experimentgroup_for_user_in_experiment(userId, experimentId)
        user = self.get_user_by_id(userId)
        if expgroup is None or user is None:
            return None
        user.experimentgroups.remove(expgroup)
        result = expgroup not in self.dbsession.query(User).filter_by(
            id=userId).first().experimentgroups and user not in expgroup.users
        return result

    def get_users_for_experimentgroup(self, experimentgroupId):
        return self.dbsession.query(ExperimentGroup).filter_by(id=experimentgroupId).first().users

    # ---------------------------------------------------------------------------------
    #                                    Dataitems
    # ---------------------------------------------------------------------------------

    def create_dataitem(self, data):
        user = data['user']
        value = data['value']
        key = data['key']
        startDatetime = datetime.datetime.strptime(data['startDatetime'], "%Y-%m-%d %H:%M:%S")
        endDatetime = datetime.datetime.strptime(data['endDatetime'], "%Y-%m-%d %H:%M:%S")
        dataitem = DataItem(
            value=value,
            key=key,
            user=user,
            startDatetime=startDatetime,
            endDatetime=endDatetime)
        self.dbsession.add(dataitem)
        return self.dbsession.query(DataItem).order_by(DataItem.id.desc()).first()

    def get_total_dataitems_for_experiment(self, experimentId):
        count = 0
        experiment = self.get_experiment(experimentId)
        for expgroup in experiment.experimentgroups:
            count += self.get_total_dataitems_for_expgroup(expgroup.id)
        return count

    def get_total_dataitems_for_expgroup(self, experimentgroupId):
        count = 0
        expgroup = self.get_experimentgroup(experimentgroupId)
        for user in expgroup.users:
            count += self.get_total_dataitems_for_user_in_experiment(user.id, expgroup.experiment_id)
        return count

    def get_total_dataitems_for_user_in_experiment(self, user_id, exp_id):
        experiment = self.get_experiment(exp_id)
        start_datetime = experiment.startDatetime
        end_datetime = experiment.endDatetime
        count = self.dbsession.query(DataItem.id).filter(
            and_(DataItem.user_id == user_id,
                 start_datetime <= DataItem.startDatetime,
                 DataItem.endDatetime <= end_datetime)).count()
        return count

    def get_dataitems_for_user(self, id):
        return self.dbsession.query(DataItem).filter_by(user_id=id)

    def get_dataitems_for_user_on_period(self, id, start_datetime, endDatetime):
        return self.dbsession.query(DataItem).filter(
            and_(DataItem.user_id == id,
                 start_datetime <= DataItem.startDatetime,
                 DataItem.endDatetime <= endDatetime)).all()

    def get_dataitems_for_user_in_experiment(self, user_id, exp_id):
        experiment = self.get_experiment(exp_id)
        start_datetime = experiment.startDatetime
        end_datetime = experiment.endDatetime
        return self.get_dataitems_for_user_on_period(user_id, start_datetime, end_datetime)

    def get_dataitems_for_experimentgroup(self, id):
        expgroup = self.get_experimentgroup(id)
        experiment = expgroup.experiment
        dataitems = []
        for user in expgroup.users:
            dataitems.extend(self.get_dataitems_for_user_in_experiment(user.id, experiment.id))
        return dataitems

    def get_dataitems_for_experiment(self, id):
        experiment = self.get_experiment(id)
        dataitems = []
        for expgroup in experiment.experimentgroups:
            dataitems.extend(self.get_dataitems_for_experimentgroup(expgroup.id))
        return dataitems

    def delete_dataitem(self, id):
        dataitem = self.dbsession.query(DataItem).filter_by(id=id).first()
        dataitem.user.dataitems.remove(dataitem)
        self.dbsession.delete(dataitem)

    # ---------------------------------------------------------------------------------
    #                                 Configurations
    # ---------------------------------------------------------------------------------

    def create_configuration(self, data):
        key = data['key']
        value = data['value']
        experimentgroup = data['experimentgroup']
        configuration = Configuration(key=key, value=value, experimentgroup=experimentgroup)
        self.dbsession.add(configuration)
        return self.dbsession.query(Configuration).order_by(Configuration.id.desc()).first()

    def delete_configuration(self, id):
        conf = self.dbsession.query(Configuration).filter_by(id=id).first()
        conf.experimentgroup.configurations.remove(conf)
        self.dbsession.delete(conf)

    def get_confs_for_experimentgroup(self, experimentgroupId):
        return self.dbsession.query(ExperimentGroup)\
            .filter_by(id=experimentgroupId).first().configurations

    def get_total_configuration_for_user(self, id):
        expgroups = self.get_experimentgroups_for_user(id)
        confs = []
        for expgroup in expgroups:
            for conf in expgroup.configurations:
                confs.append(conf)
        return confs
