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
            self.delete_experiment_group_in_users(experimentgroup.id)
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
        dateTimeNow = datetime.datetime.now()
        startDatetime = experiment.startDatetime
        endDatetime = experiment.endDatetime
        if startDatetime >= endDatetime:
            # validate this earlier
            return None
        if startDatetime <= dateTimeNow and dateTimeNow <= endDatetime:
            return running
        elif dateTimeNow > endDatetime:
            return finished
        elif dateTimeNow < startDatetime:
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
        experimentgroups = self.getExperimentgroupsForUser(id)
        experiments = []
        for experimentgroup in experimentgroups:
            experiments.append(experimentgroup.experiment)
        return experiments

    # ---------------------------------------------------------------------------------
    #                                 ExperimentGroups
    # ---------------------------------------------------------------------------------

    def create_experiment_group(self, data):
        name = data['name']
        experimentgroup = ExperimentGroup(name=name)
        self.dbsession.add(experimentgroup)
        return self.dbsession.query(ExperimentGroup).order_by(ExperimentGroup.id.desc()).first()

    def delete_experiment_group(self, id):
        experimentgroup = self.dbsession.query(ExperimentGroup).filter_by(id=id).first()
        if experimentgroup is None:
            return False
        self.delete_experiment_group_in_users(id)
        experimentgroup.experiment.experimentgroups.remove(experimentgroup)
        self.dbsession.delete(experimentgroup)
        return [] == self.dbsession.query(ExperimentGroup).filter_by(id=id).all()

    def delete_experiment_group_in_users(self, experimentgroupId):
        experimentgroup = self.get_experimentgroup(experimentgroupId)
        if experimentgroup is None:
            return False
        for user in experimentgroup.users:
            user.experimentgroups.remove(experimentgroup)

    def get_experimentgroup(self, id):
        return self.dbsession.query(ExperimentGroup).filter_by(id=id).first()

    def get_experimentgroups(self, id):
        return self.dbsession.query(ExperimentGroup).filter_by(experiment_id=id).all()

    def get_experimentgroup_for_user_in_experiment(self, userId, experimentId):
        expgroups = self.getExperimentgroupsForUser(userId)
        if expgroups is None:
            return None
        for expgroup in expgroups:
            if expgroup.experiment_id == experimentId:
                return expgroup

    def getExperimentgroupsForUser(self, id):
        user = self.dbsession.query(User).filter_by(id=id).first()
        if user is None:
            return None
        return user.experimentgroups

    # ---------------------------------------------------------------------------------
    #                                      Users
    # ---------------------------------------------------------------------------------

    def createUser(self, data):
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

    def getUserById(self, id):
        return self.dbsession.query(User).filter_by(id=id).first()

    def getUserByUsername(self, username):
        return self.dbsession.query(User).filter_by(username=username).first()

    def getAllUsers(self):
        return self.dbsession.query(User).all()

    def deleteUser(self, id):
        user = self.dbsession.query(User).filter_by(id=id).first()
        if user is None:
            return False
        for experimentgroup in user.experimentgroups:
            experimentgroup.users.remove(user)
        self.dbsession.delete(user)
        return [] == self.dbsession.query(User).filter_by(id=id).all()

    def getUser(self, username):
        user = self.dbsession.query(User).filter_by(username=username).all()
        if user == []:
            return self.createUser({'username': username})
        else:
            return user[0]

    def assignUserToExperiment(self, userId, experimentId):
        experimentgroups = self.get_experimentgroups(experimentId)
        if len(experimentgroups) == 1:
            experimentgroup = experimentgroups[0]
        else:
            experimentgroup = experimentgroups[random.randint(0, len(experimentgroups) - 1)]
        self.dbsession.query(User)\
            .filter_by(id=userId).first()\
            .experimentgroups.append(experimentgroup)

    def assignUserToExperiments(self, id):
        # We are (now) assigning users only for running experiments
        allExperiments = self.get_all_running_experiments()
        experimentsUserParticipates = self.get_experiments_user_participates(id)
        experimentsUserDoesNotParticipate = []
        for experiment in allExperiments:
            if experiment not in experimentsUserParticipates:
                experimentsUserDoesNotParticipate.append(experiment)
        experimentsUserShouldParticipate = experimentsUserDoesNotParticipate
        for experiment in experimentsUserShouldParticipate:
            self.assignUserToExperiment(id, experiment.id)

    def getUsersForExperiment(self, id):
        experiment = self.get_experiment(id)
        if experiment is None:
            return None
        users = []
        for experimentgroup in experiment.experimentgroups:
            users.extend(experimentgroup.users)
        return users

    def deleteUserFromExperiment(self, userId, experimentId):
        expgroup = self.get_experimentgroup_for_user_in_experiment(userId, experimentId)
        user = self.getUserById(userId)
        if expgroup is None or user is None:
            return None
        user.experimentgroups.remove(expgroup)
        result = expgroup not in self.dbsession.query(User).filter_by(
            id=userId).first().experimentgroups and user not in expgroup.users
        return result

    def getUsersForExperimentgroup(self, experimentgroupId):
        return self.dbsession.query(ExperimentGroup).filter_by(id=experimentgroupId).first().users

    # ---------------------------------------------------------------------------------
    #                                    Dataitems
    # ---------------------------------------------------------------------------------

    def createDataitem(self, data):
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

    def getTotalDataitemsForExperiment(self, experimentId):
        count = 0
        experiment = self.get_experiment(experimentId)
        for expgroup in experiment.experimentgroups:
            count += self.getTotalDataitemsForExpgroup(expgroup.id)
        return count

    def getTotalDataitemsForExpgroup(self, experimentgroupId):
        count = 0
        expgroup = self.get_experimentgroup(experimentgroupId)
        for user in expgroup.users:
            count += self.getTotalDataitemsForUserInExperiment(user.id, expgroup.experiment_id)
        return count

    def getTotalDataitemsForUserInExperiment(self, userId, expId):
        experiment = self.get_experiment(expId)
        startDatetime = experiment.startDatetime
        endDatetime = experiment.endDatetime
        count = self.dbsession.query(DataItem.id).filter(
            and_(DataItem.user_id == userId,
                 startDatetime <= DataItem.startDatetime,
                 DataItem.endDatetime <= endDatetime)).count()
        return count

    def getDataitemsForUser(self, id):
        return self.dbsession.query(DataItem).filter_by(user_id=id)

    def getDataitemsForUserOnPeriod(self, id, startDatetime, endDatetime):
        return self.dbsession.query(DataItem).filter(
            and_(DataItem.user_id == id,
                 startDatetime <= DataItem.startDatetime,
                 DataItem.endDatetime <= endDatetime)).all()

    def getDataitemsForUserInExperiment(self, userId, expId):
        experiment = self.get_experiment(expId)
        startDatetime = experiment.startDatetime
        endDatetime = experiment.endDatetime
        return self.getDataitemsForUserOnPeriod(userId, startDatetime, endDatetime)

    def getDataitemsForExperimentgroup(self, id):
        expgroup = self.get_experimentgroup(id)
        experiment = expgroup.experiment
        dataitems = []
        for user in expgroup.users:
            dataitems.extend(self.getDataitemsForUserInExperiment(user.id, experiment.id))
        return dataitems

    def getDataitemsForExperiment(self, id):
        experiment = self.get_experiment(id)
        dataitems = []
        for expgroup in experiment.experimentgroups:
            dataitems.extend(self.getDataitemsForExperimentgroup(expgroup.id))
        return dataitems

    def deleteDataitem(self, id):
        dataitem = self.dbsession.query(DataItem).filter_by(id=id).first()
        dataitem.user.dataitems.remove(dataitem)
        self.dbsession.delete(dataitem)

    # ---------------------------------------------------------------------------------
    #                                 Configurations
    # ---------------------------------------------------------------------------------

    def createConfiguration(self, data):
        key = data['key']
        value = data['value']
        experimentgroup = data['experimentgroup']
        configuration = Configuration(key=key, value=value, experimentgroup=experimentgroup)
        self.dbsession.add(configuration)
        return self.dbsession.query(Configuration).order_by(Configuration.id.desc()).first()

    def deleteConfiguration(self, id):
        conf = self.dbsession.query(Configuration).filter_by(id=id).first()
        conf.experimentgroup.configurations.remove(conf)
        self.dbsession.delete(conf)

    def getConfsForExperimentgroup(self, experimentgroupId):
        return self.dbsession.query(ExperimentGroup)\
            .filter_by(id=experimentgroupId).first().configurations

    def getTotalConfigurationForUser(self, id):
        expgroups = self.getExperimentgroupsForUser(id)
        confs = []
        for expgroup in expgroups:
            for conf in expgroup.configurations:
                confs.append(conf)
        return confs
