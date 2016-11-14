""" import modules """
import random
import datetime
from sqlalchemy import and_
from sqlalchemy import func
from experiment_server.models.experimentgroups import ExperimentGroup
from experiment_server.models.experiments import Experiment
from experiment_server.models.clients import Client
from experiment_server.models.dataitems import DataItem
from experiment_server.models.configurations import Configuration



"""
    WARNING: This is a depricated class. Currently this works only as helper
    class for tests.
"""

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
        experiment = Experiment(
            name=name,
            startDatetime=start_datetime,
            endDatetime=end_datetime,
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
            self.delete_experimentgroup_in_clients(experimentgroup.id)
        self.dbsession.delete(experiment)
        return [] == self.dbsession.query(Experiment).filter_by(id=id).all()

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

    def get_all_running_experiments(self):
        """ get all running experiments by comparing now and start time, also now and end time """
        date_time_now = datetime.datetime.now()
        return self.dbsession.query(Experiment).filter(
            and_(Experiment.startDatetime <= date_time_now,
                 date_time_now <= Experiment.endDatetime)).all()

    def get_client_experiments_list(self, id):
        """ return the experiment list of specific client """
        experimentgroups = self.get_experimentgroups_for_client(id)
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
        self.delete_experimentgroup_in_clients(id)
        experimentgroup.experiment.experimentgroups.remove(experimentgroup)
        self.dbsession.delete(experimentgroup)
        return [] == self.dbsession.query(ExperimentGroup).filter_by(id=id).all()

    def delete_experimentgroup_in_clients(self, experimentgroup_id):
        """ delete experiment group in every client """
        experimentgroup = ExperimentGroup.get(experimentgroup_id)
        if experimentgroup is None:
            return False
        for client in experimentgroup.clients:
            client.experimentgroups.remove(experimentgroup)

    def get_experimentgroup_for_client_in_experiment(self, client_id, experiment_id):
        """ get experiment group from experiment groups if client is in the experiment """
        expgroups = self.get_experimentgroups_for_client(client_id)
        if expgroups is None:
            return None
        for expgroup in expgroups:
            if expgroup.experiment_id == experiment_id:
                return expgroup

    def get_experimentgroups_for_client(self, id):
        """ get client's experiment groups """
        client = self.dbsession.query(Client).filter_by(id=id).first()
        if client is None:
            return None
        return client.experimentgroups

    # ---------------------------------------------------------------------------------
    #                                      clients
    # ---------------------------------------------------------------------------------

    def create_client(self, data):
        """ create client """
        keys = ['clientname', 'password', 'experimentgroups', 'dataitems']
        for key in keys:
            try:
                data[key]
            except KeyError:
                data[key] = []
        client = Client(clientname=data['clientname'],
                    experimentgroups=data['experimentgroups'],
                    dataitems=data['dataitems'])
        self.dbsession.add(client)
        return self.dbsession.query(Client).order_by(Client.id.desc()).first()

    def delete_client(self, id):
        """ delete client by id """
        client = self.dbsession.query(Client).filter_by(id=id).first()
        if client is None:
            return False
        for experimentgroup in client.experimentgroups:
            experimentgroup.clients.remove(client)
        self.dbsession.delete(client)
        return [] == self.dbsession.query(Client).filter_by(id=id).all()

    def get_client(self, clientname):
        """ get client by clientname """
        client = self.dbsession.query(Client).filter_by(clientname=clientname).all()
        if not client:
            return self.create_client({'clientname': clientname})
        else:
            return client[0]

    def assign_client_to_experiment(self, client_id, experiment_id):
        """ randomly assign client to different experiment """
        experimentgroups = Experiment.get(experiment_id).experimentgroups
        if len(experimentgroups) == 1:
            experimentgroup = experimentgroups[0]
        else:
            experimentgroup = experimentgroups[random.randint(0, len(experimentgroups) - 1)]
        self.dbsession.query(Client)\
            .filter_by(id=client_id).first()\
            .experimentgroups.append(experimentgroup)

    def assign_client_to_experiments(self, id):
        """ We are (now) assigning clients only for running experiments """
        all_experiments = self.get_all_running_experiments()
        experiments_client_participates = self.get_client_experiments_list(id)
        experiments_client_does_not_participate = []
        for experiment in all_experiments:
            if experiment not in experiments_client_participates:
                experiments_client_does_not_participate.append(experiment)
        experiments_client_should_participate = experiments_client_does_not_participate
        for experiment in experiments_client_should_participate:
            self.assign_client_to_experiment(id, experiment.id)

    def get_clients_for_experiment(self, id):
        """ get clients from the specific experiment """
        experiment = Experiment.get(id)
        if experiment is None:
            return None
        clients = []
        for experimentgroup in experiment.experimentgroups:
            clients.extend(experimentgroup.clients)
        return clients

    def delete_client_from_experiment(self, client_id, experiment_id):
        """ delete client from experiment """
        expgroup = self.get_experimentgroup_for_client_in_experiment(client_id, experiment_id)
        client = Client.get(client_id)
        if expgroup is None or client is None:
            return None
        client.experimentgroups.remove(expgroup)
        result = expgroup not in self.dbsession.query(Client).filter_by(
            id=client_id).first().experimentgroups and client not in expgroup.clients
        return result

    def get_clients_for_experimentgroup(self, experimentgroup_id):
        """ get all clients from specific experiment group """
        return self.dbsession.query(ExperimentGroup).filter_by(id=experimentgroup_id).first().clients

    # ---------------------------------------------------------------------------------
    #                                    Dataitems
    # ---------------------------------------------------------------------------------

    def create_dataitem(self, data):
        """ create dataitem """
        client = data['client']
        value = data['value']
        key = data['key']
        start_datetime = datetime.datetime.strptime(data['startDatetime'], "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.datetime.strptime(data['endDatetime'], "%Y-%m-%d %H:%M:%S")
        dataitem = DataItem(
            value=value,
            key=key,
            client=client,
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
        for client in expgroup.clients:
            count += self.get_total_dataitems_for_client_in_experiment(client.id,
                                                                     expgroup.experiment_id)
        return count

    def get_total_dataitems_for_client_in_experiment(self, client_id, exp_id):
        """ get total dataitems for specific client in specific experiment """
        experiment = Experiment.get(exp_id)
        start_datetime = experiment.startDatetime
        end_datetime = experiment.endDatetime
        count = DataItem.query().filter(
            and_(DataItem.client_id == client_id,
                 start_datetime <= DataItem.startDatetime,
                 DataItem.endDatetime <= end_datetime)).count()
        return count

    def get_dataitems_for_client_on_period(self, id, start_datetime, end_datetime):
        """ get dataitems from specific client on a specific period """
        return self.dbsession.query(DataItem).filter(
            and_(DataItem.client_id == id,
                 start_datetime <= DataItem.startDatetime,
                 DataItem.endDatetime <= end_datetime)).all()

    def get_dataitems_for_client_in_experiment(self, client_id, exp_id):
        """ get dataitems from specific client in specific experiment """
        experiment = Experiment.get(exp_id)
        start_datetime = experiment.startDatetime
        end_datetime = experiment.endDatetime
        return self.get_dataitems_for_client_on_period(client_id, start_datetime, end_datetime)

    def get_dataitems_for_experimentgroup(self, id):
        """ get dataitems list from a specific experiment group """
        expgroup = ExperimentGroup.get(id)
        experiment = expgroup.experiment
        dataitems = []
        for client in expgroup.clients:
            dataitems.extend(self.get_dataitems_for_client_in_experiment(client.id, experiment.id))
        return dataitems

    def get_dataitems_for_experiment(self, id):
        """ get dataitems list from a specific experiment """
        experiment = Experiment.get(id)
        dataitems = []
        for expgroup in experiment.experimentgroups:
            dataitems.extend(self.get_dataitems_for_experimentgroup(expgroup.id))
        return dataitems

    def delete_dataitem(self, id):
        """ delete one dataitem """
        dataitem = self.dbsession.query(DataItem).filter_by(id=id).first()
        dataitem.client.dataitems.remove(dataitem)
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

    def get_total_configuration_for_client(self, id):
        """ get all configurations list from experiment groups """
        expgroups = self.get_experimentgroups_for_client(id)
        confs = []
        for expgroup in expgroups:
            for conf in expgroup.configurations:
                confs.append(conf)
        return confs
