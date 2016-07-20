from .experimentgroups import ExperimentGroup
from .experiments import Experiment
from .users import User
from .dataitems import DataItem
from .configurations import Configuration
import random
from datetime import datetime

class DatabaseInterface:
	def __init__(self, dbsession):
		self.dbsession = dbsession

#---------------------------------------------------------------------------------
#                                   Experiments                                   
#---------------------------------------------------------------------------------
	def createExperiment(self, data): #CHECK
		name = data['name']
		experimentgroups = data['experimentgroups']
		startDatetime = datetime.strptime(data['startDatetime'], "%Y-%m-%d %H:%M:%S")
		endDatetime = datetime.strptime(data['endDatetime'], "%Y-%m-%d %H:%M:%S")
		size = data['size']
		if (startDatetime is not None and endDatetime is not None):
			experiment = Experiment(name=name, startDatetime=startDatetime, endDatetime=endDatetime)
		else:
			experiment = Experiment(name=name)
		if (size is not None):
			experiment.size = size
		for experimentgroup in experimentgroups:
			experiment.experimentgroups.append(experimentgroup)
		self.dbsession.add(experiment)
		return experiment

	def getAllExperiments(self): #OK
		return self.dbsession.query(Experiment).all()

	def getExperiment(self, id): #OK
		return self.dbsession.query(Experiment).filter_by(id=id).one()

	def deleteExperiment(self, id): #CHECK
	#Deletes also experimentgroups in experiment
		experiment = self.dbsession.query(Experiment).filter_by(id=id).one()
		experimentgroups = experiment.experimentgroups
		for experimentgroup in experimentgroups:
			self.deleteExperimentgroupInUsers(experimentgroup.id)
		self.dbsession.delete(experiment)

	def getUsersInExperiment(self, id): #CHECK
		experimentgroups = self.dbsession.query(Experiment).filter_by(id=id).one().experimentgroups
		users = []
		for experimentgroup in experimentgroups:
			users.extend(experimentgroup.users)
		return users

	def deleteUserFromExperiment(self, userId, experimentId):
		expgroup = self.getExperimentgroupForUserInExperiment(userId, experimentId)
		user = self.getUser(userId)
		user.experimentgroups.remove(expgroup)

#---------------------------------------------------------------------------------
#                                 ExperimentGroups                                
#---------------------------------------------------------------------------------

	def createExperimentgroup(self, data): #OK
		name = data['name']
		experimentgroup = ExperimentGroup(name=name)
		self.dbsession.add(experimentgroup)
		return experimentgroup

	def deleteExperimentgroup(self, id): #CHECK
		experimentgroup = self.dbsession.query(ExperimentGroup).filter_by(id=id).one()
		"""
		confs = experimentgroup.configurations
		for conf in confs:
			self.deleteConfiguration(conf.id)
		"""
		self.deleteExperimentgroupInUsers(id)
		self.dbsession.delete(experimentgroup)

	def deleteExperimentgroupInUsers(self, experimentgroupId): #OK
		experimentgroup = self.getExperimentgroup(experimentgroupId)
		for user in experimentgroup.users:
				user.experimentgroups.remove(experimentgroup)

	def getExperimentgroup(self, id): #OK
		return self.dbsession.query(ExperimentGroup).filter_by(id=id).one()

	def getExperimentgroups(self, id): #OK
		return self.dbsession.query(ExperimentGroup).filter_by(experiment_id = id).all()

	def getUsersInExperimentgroup(self, experimentgroupId): #OK
		return self.dbsession.query(ExperimentGroup).filter_by(id=experimentgroupId).one().users

	def getConfForExperimentgroup(self, experimentgroupId): #OK
		return self.dbsession.query(ExperimentGroup).filter_by(id=experimentgroupId).one().configuration

	def getExperimentgroupForUserInExperiment(self, userId, experimentId):
		expgroups = self.getExperimentgroupsForUser(userId)
		for expgroup in expgroups:
			if expgroup.experiment_id == experimentId:
				return expgroup

#---------------------------------------------------------------------------------
#                                      Users                                      
#---------------------------------------------------------------------------------

	def createUser(self, data): #CHECK
		keys = ['username', 'password', 'experimentgroups', 'dataitems']
		for key in keys:
			try:
				data[key]
			except KeyError:
				data[key] = []
		user = User(username=data['username'], experimentgroups=data['experimentgroups'], dataitems=data['dataitems'])
		self.dbsession.add(user)
		return self.dbsession.query(User).filter_by(username=data['username']).one()

	def getUser(self, id): #OK
		return self.dbsession.query(User).filter_by(id=id).one()

	def getUserByUsername(self, username):
		return self.dbsession.query(User).filter_by(username=username).one()

	def getAllUsers(self): #OK
		return self.dbsession.query(User).all()

	def getExperimentsUserParticipates(self, id): #CHECK
		experimentgroups = self.getExperimentgroupsForUser(id)
		experiments = []
		for experimentgroup in experimentgroups:
			experiments.append(experimentgroup.experiment)
		return experiments

	def getExperimentgroupsForUser(self, id):
		return self.dbsession.query(User).filter_by(id=id).one().experimentgroups

	def deleteUser(self, id): #CHECK
		user = self.dbsession.query(User).filter_by(id=id).one()
		"""
		dataitems = user.dataitems
		for dataitem in dataitems:
			self.dbsession.deleteDataitem(dataitem.id)
		"""
		self.dbsession.delete(user)

	def getDataitemsForUser(self, id): #OK
		return self.dbsession.query(DataItem).filter_by(user_id=id)

	def checkUser(self, username): #OK
		user = self.dbsession.query(User).filter_by(username=username).all()
		if user == []:
			return self.createUser({'username':username})
		else:
			return user[0]

	def getConfigurationForUser(self, id): #CHECK
		expgroups = self.getExperimentgroupsForUser(id)
		confs = []
		for expgroup in expgroups:
		    for conf in expgroup.configurations:
		        confs.append(conf)
		return confs

	def assignUserToExperiment(self, data):
		userId = data['user']
		experimentId = data['experiment']
		experimentgroups = self.getExperimentgroups(experimentId)
		experimentgroup = experimentgroups[random.randint(0, len(experimentgroups)-1)]
		self.dbsession.query(User).filter_by(id=userId).one().experimentgroups.append(experimentgroup)

	def assignUserToExperiments(self, id):
		allExperiments = self.getAllExperiments()
		experimentsUserParticipates = self.getExperimentsUserParticipates(id)
		experimentsUserDoesNotParticipate = []
		for experiment in allExperiments:
			if experiment not in experimentsUserParticipates:
				experimentsUserDoesNotParticipate.append(experiment)
		for experiment in experimentsUserDoesNotParticipate:
			self.assignUserToExperiment({'user':id, 'experiment':experiment.id})

#---------------------------------------------------------------------------------
#                                    Dataitems                                     
#---------------------------------------------------------------------------------
	
	def createDataitem(self, data): #CHECK
		userId = data['user']
		value = data['value']
		key = data['key']
		dataitem = DataItem(value=value, key=key, user=self.getUser(userId))
		self.dbsession.add(dataitem)
		return dataitem

	def getTotalDataitemsForExperiment(self, experimentId):
		return 100

	def getTotalDataitemsForExpgroup(self, experimentgroupId):
		return 25

	def getTotalDataitemsForUser(self, userId):
		return 10

	def deleteDataitem(self, id):
		dataitem = self.dbsession.query(DataItem).filter_by(id=id).one()
		self.dbsession.delete(dataitem)

#---------------------------------------------------------------------------------
#                                 Configurations                                  
#---------------------------------------------------------------------------------

	def createConfiguration(self, data): #CHECK
		key = data['key']
		value = data['value']
		experimentgroup = data['experimentgroup']
		configuration = Configuration(key=key, value=value, experimentgroup=experimentgroup)
		self.dbsession.add(configuration)
		return configuration

	def deleteConfiguration(self, id):
		conf = self.dbsession.query(Configuration).filter_by(id=id).one()
		self.dbsession.delete(conf)


	#TODO getUsersInConfiguration?
