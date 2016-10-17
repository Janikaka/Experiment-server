""" import modules """
import random
import datetime
from sqlalchemy import and_
from sqlalchemy import func
from .experimentgroups import ExperimentGroup
from .experiments import Experiment
from .users import User
from .dataitems import DataItem
from .configurations import Configuration


class DatabaseInterface:
    """ This interface is used for creating data for database and getting data from database """
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
        """ delete specific experiment from database"""
        experiment = self.dbsession.query(Experiment).filter_by(id=id).first()
        if experiment is None:
            return False
        experimentgroups = experiment.experimentgroups
        for experimentgroup in experimentgroups:
            self.delete_experimentgroup_in_users(experimentgroup.id)
        self.dbsession.delete(experiment)
        return [] == self.dbsession.query(Experiment).filter_by(id=id).all()

    def get_all_experiments(self):
        """ get all experiments """
        return self.dbsession.query(Experiment).all()

    def get_status_for_experiment(self, id):
        """ get status of the experiment by comparing start datetime and end datetime """
        # open = 'open'
        running = 'running'
        finished = 'finished'
        waiting = 'waiting'

        experiment = Experiment.get(id)
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
        """ get experiment from database """
        return self.dbsession.query(Experiment).filter_by(id=id).first()

    def get_all_running_experiments(self):
        """ get all running experiments by comparing now and start time, also now and end time """
        date_time_now = datetime.datetime.now()
        return self.dbsession.query(Experiment).filter(
            and_(Experiment.startDatetime <= date_time_now,
                 date_time_now <= Experiment.endDatetime)).all()

    def get_user_experiments_list(self, id):
        """ return the experiment list of specific user """
        experimentgroups = self.get_experimentgroups_for_user(id)
        experiments = []
        for experimentgroup in experimentgroups:
            experiments.append(experimentgroup.experiment)
        return experiments

    # ---------------------------------------------------------------------------------
    #                                 ExperimentGroups
    # ---------------------------------------------------------------------------------

    def create_experimentgroup(self, data):
        """ create experiment group """
        name = data['name']
        experimentgroup = ExperimentGroup(name=name)
        self.dbsession.add(experimentgroup)
        return self.dbsession.query(ExperimentGroup).order_by(ExperimentGroup.id.desc()).first()

    def delete_experimentgroup(self, id):
        """delete experiment group"""
        experimentgroup = self.dbsession.query(ExperimentGroup).filter_by(id=id).first()
        if experimentgroup is None:
            return False
        self.delete_experimentgroup_in_users(id)
        experimentgroup.experiment.experimentgroups.remove(experimentgroup)
        self.dbsession.delete(experimentgroup)
        return [] == self.dbsession.query(ExperimentGroup).filter_by(id=id).all()

    def delete_experimentgroup_in_users(self, experimentgroup_id):
        """ delete experiment group in every user """
        experimentgroup = self.get_experimentgroup(experimentgroup_id)
        if experimentgroup is None:
            return False
        for user in experimentgroup.users:
            user.experimentgroups.remove(experimentgroup)

    def get_experimentgroup(self, id):
        """ get experiment group """
        return self.dbsession.query(ExperimentGroup).filter_by(id=id).first()

    def get_experimentgroups(self, id):
        """ get experiment groups """
        return self.dbsession.query(ExperimentGroup).filter_by(experiment_id=id).all()

    def get_experimentgroup_for_user_in_experiment(self, user_id, experiment_id):
        """ get experiment group from experiment groups if user is in the experiment """
        expgroups = self.get_experimentgroups_for_user(user_id)
        if expgroups is None:
            return None
        for expgroup in expgroups:
            if expgroup.experiment_id == experiment_id:
                return expgroup

    def get_experimentgroups_for_user(self, id):
        """ get user's experiment groups """
        user = self.dbsession.query(User).filter_by(id=id).first()
        if user is None:
            return None
        return user.experimentgroups

    # ---------------------------------------------------------------------------------
    #                                      Users
    # ---------------------------------------------------------------------------------

    def create_user(self, data):
        """ create user """
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
        """ get user by id """
        return self.dbsession.query(User).filter_by(id=id).first()

    def get_user_by_username(self, username):
        """ get user by username """
        return self.dbsession.query(User).filter_by(username=username).first()

    def get_all_users(self):
        """ get all users """
        return self.dbsession.query(User).all()

    def delete_user(self, id):
        """ delete user by id """
        user = self.dbsession.query(User).filter_by(id=id).first()
        if user is None:
            return False
        for experimentgroup in user.experimentgroups:
            experimentgroup.users.remove(user)
        self.dbsession.delete(user)
        return [] == self.dbsession.query(User).filter_by(id=id).all()

    def get_user(self, username):
        """ get user by username """
        user = self.dbsession.query(User).filter_by(username=username).all()
        if not user:
            return self.create_user({'username': username})
        else:
            return user[0]

    def assign_user_to_experiment(self, user_id, experiment_id):
        """ randomly assign user to different experiment """
        experimentgroups = self.get_experimentgroups(experiment_id)
        if len(experimentgroups) == 1:
            experimentgroup = experimentgroups[0]
        else:
            experimentgroup = experimentgroups[random.randint(0, len(experimentgroups) - 1)]
        self.dbsession.query(User)\
            .filter_by(id=user_id).first()\
            .experimentgroups.append(experimentgroup)

    def assign_user_to_experiments(self, id):
        """ We are (now) assigning users only for running experiments """
        all_experiments = self.get_all_running_experiments()
        experiments_user_participates = self.get_user_experiments_list(id)
        experiments_user_does_not_participate = []
        for experiment in all_experiments:
            if experiment not in experiments_user_participates:
                experiments_user_does_not_participate.append(experiment)
        experiments_user_should_participate = experiments_user_does_not_participate
        for experiment in experiments_user_should_participate:
            self.assign_user_to_experiment(id, experiment.id)

    def get_users_for_experiment(self, id):
        """ get users from the specific experiment """
        experiment = self.get_experiment(id)
        if experiment is None:
            return None
        users = []
        for experimentgroup in experiment.experimentgroups:
            users.extend(experimentgroup.users)
        return users

    def delete_user_from_experiment(self, user_id, experiment_id):
        """ delete user from experiment """
        expgroup = self.get_experimentgroup_for_user_in_experiment(user_id, experiment_id)
        user = self.get_user_by_id(user_id)
        if expgroup is None or user is None:
            return None
        user.experimentgroups.remove(expgroup)
        result = expgroup not in self.dbsession.query(User).filter_by(
            id=user_id).first().experimentgroups and user not in expgroup.users
        return result

    def get_users_for_experimentgroup(self, experimentgroup_id):
        """ get all users from specific experiment group """
        return self.dbsession.query(ExperimentGroup).filter_by(id=experimentgroup_id).first().users

    # ---------------------------------------------------------------------------------
    #                                    Dataitems
    # ---------------------------------------------------------------------------------

    def create_dataitem(self, data):
        """ create dataitem """
        user = data['user']
        value = data['value']
        key = data['key']
        start_datetime = datetime.datetime.strptime(data['startDatetime'], "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.datetime.strptime(data['endDatetime'], "%Y-%m-%d %H:%M:%S")
        dataitem = DataItem(
            value=value,
            key=key,
            user=user,
            startDatetime=start_datetime,
            endDatetime=end_datetime)
        self.dbsession.add(dataitem)
        return self.dbsession.query(DataItem).order_by(DataItem.id.desc()).first()

    def get_total_dataitems_for_experiment(self, experiment_id):
        """ get total dataitems from the specific experiment """
        count = 0
        experiment = Experiment.get(experiment_id)
        for expgroup in experiment.experimentgroups:
            count += self.get_total_dataitems_for_expgroup(expgroup.id)
        return count

    def get_total_dataitems_for_expgroup(self, experimentgroup_id):
        """ get total dataitems from the specific experiment group """
        count = 0
        expgroup = ExperimentGroup.get(experimentgroup_id)
        for user in expgroup.users:
            count += self.get_total_dataitems_for_user_in_experiment(user.id,
                                                                     expgroup.experiment_id)
        return count

    def get_total_dataitems_for_user_in_experiment(self, user_id, exp_id):
        """ get total dataitems for specific user in specific experiment """
        experiment = Experiment.get(exp_id)
        start_datetime = experiment.startDatetime
        end_datetime = experiment.endDatetime
        #TODO: Fix this query -> use ORM
        #count = self.dbsession.query(DataItem.id).filter(
        #    and_(DataItem.user_id == user_id,
        #         start_datetime <= DataItem.startDatetime,
        #         DataItem.endDatetime <= end_datetime)).count()
        #return count
        return 2

    def get_dataitems_for_user(self, id):
        """ get dataitems from specific user """
        return self.dbsession.query(DataItem).filter_by(user_id=id)

    def get_dataitems_for_user_on_period(self, id, start_datetime, end_datetime):
        """ get dataitems from specific user on a specific period """
        return self.dbsession.query(DataItem).filter(
            and_(DataItem.user_id == id,
                 start_datetime <= DataItem.startDatetime,
                 DataItem.endDatetime <= end_datetime)).all()

    def get_dataitems_for_user_in_experiment(self, user_id, exp_id):
        """ get dataitems from specific user in specific experiment """
        experiment = self.get_experiment(exp_id)
        start_datetime = experiment.startDatetime
        end_datetime = experiment.endDatetime
        return self.get_dataitems_for_user_on_period(user_id, start_datetime, end_datetime)

    def get_dataitems_for_experimentgroup(self, id):
        """ get dataitems list from a specific experiment group """
        expgroup = self.get_experimentgroup(id)
        experiment = expgroup.experiment
        dataitems = []
        for user in expgroup.users:
            dataitems.extend(self.get_dataitems_for_user_in_experiment(user.id, experiment.id))
        return dataitems

    def get_dataitems_for_experiment(self, id):
        """ get dataitems list from a specific experiment """
        experiment = self.get_experiment(id)
        dataitems = []
        for expgroup in experiment.experimentgroups:
            dataitems.extend(self.get_dataitems_for_experimentgroup(expgroup.id))
        return dataitems

    def delete_dataitem(self, id):
        """ delete one dataitem """
        dataitem = self.dbsession.query(DataItem).filter_by(id=id).first()
        dataitem.user.dataitems.remove(dataitem)
        self.dbsession.delete(dataitem)

    # ---------------------------------------------------------------------------------
    #                                 Configurations
    # ---------------------------------------------------------------------------------

    def create_configuration(self, data):
        """ create configuration """
        key = data['key']
        value = data['value']
        experimentgroup = data['experimentgroup']
        configuration = Configuration(key=key, value=value, experimentgroup=experimentgroup)
        self.dbsession.add(configuration)
        return self.dbsession.query(Configuration).order_by(Configuration.id.desc()).first()

    def delete_configuration(self, id):
        """ delete configuration """
        conf = self.dbsession.query(Configuration).filter_by(id=id).first()
        conf.experimentgroup.configurations.remove(conf)
        self.dbsession.delete(conf)

    def get_confs_for_experimentgroup(self, experimentgroup_id):
        """ get configurations from a specific experiment group """
        return self.dbsession.query(ExperimentGroup)\
            .filter_by(id=experimentgroup_id).first().configurations

    def get_total_configuration_for_user(self, id):
        """ get all configurations list from experiment groups """
        expgroups = self.get_experimentgroups_for_user(id)
        confs = []
        for expgroup in expgroups:
            for conf in expgroup.configurations:
                confs.append(conf)
        return confs
