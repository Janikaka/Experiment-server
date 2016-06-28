from .experimentGroups import ExperimentGroups
from .experiments import Experiments
from .users import Users
from .dataItems import DataItems
from .configurations import Configurations

class DatabaseInterface:
	def __init__(self, dbsession):
		self.dbsession = dbsession

#---------------------------------------------------------------------------------
#                                   Experiments                                   
#---------------------------------------------------------------------------------
	def createExperiment(self, data): #CHECK
		name = data['name']
		experimentgroups = data['experimentgroups']
		experiment = Experiments(name=name)
		for experimentgroup in experimentgroups:
			experiment.experimentgroups.append(experimentgroup)
		self.dbsession.add(experiment)
		return experiment

	def getAllExperiments(self): #OK
		return self.dbsession.query(Experiments).all()

	def getExperiment(self, id): #OK
		return self.dbsession.query(Experiments).filter_by(id=id).one()

	def deleteExperiment(self, id): #CHECK
	#Deletes also experimentgroups in experiment
		print("TÄÄLLLÄÄÄ DELETEEE EXPERIMENT")
		experiment = self.dbsession.query(Experiments).filter_by(id=id).one()
		experimentgroups = experiment.experimentgroups
		for experimentgroup in experimentgroups:
			self.deleteExperimentgroupInUsers(experimentgroup.id)
		self.dbsession.delete(experiment)

	def getUsersInExperiment(self, id): #CHECK
		experimentgroups = self.dbsession.query(Experiments).filter_by(id=id).one().experimentgroups
		users = []
		for experimentgroup in experimentgroups:
			users.extend(experimentgroup.users)
		return users

#---------------------------------------------------------------------------------
#                                 ExperimentGroups                                
#---------------------------------------------------------------------------------

	def createExperimentgroup(self, data): #OK
		name = data['name']
		experimentgroup = ExperimentGroups(name=name)
		self.dbsession.add(experimentgroup)
		return experimentgroup

	def deleteExperimentgroup(self, id): #CHECK
		experimentgroup = self.dbsession.query(ExperimentGroups).filter_by(id=id).one()
		self.deleteExperimentgroupInUsers(id)
		self.dbsession.delete(experimentgroup)

	def deleteExperimentgroupInUsers(self, experimentgroupId): #OK
		experimentgroup = self.getExperimentgroup(experimentgroupId)
		for user in experimentgroup.users:
				user.experimentgroups.remove(experimentgroup)

	def getExperimentgroup(self, id): #OK
		return self.dbsession.query(ExperimentGroups).filter_by(id=id).one()

	def getExperimentgroups(self, id): #OK
		return self.dbsession.query(ExperimentGroups).filter_by(experiment_id = id)

	def getUsersInExperimentgroup(self, experimentgroupID): #OK
		return self.dbsession.query(ExperimentGroups).filter_by(id=experimentgroupID).one().users

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
		user = Users(username=data['username'], password=data['password'], experimentgroups=data['experimentgroups'], dataitems=data['dataitems'])
		self.dbsession.add(user)
		return user

	def getUser(self, id): #OK
		return self.dbsession.query(Users).filter_by(id=id).one()

	def getAllUsers(self): #OK
		return self.dbsession.query(Users).all()

	def getExperimentsForUser(self, id): #CHECK
		experimentgroups = self.dbsession.query(Users).filter_by(id=id).one().experimentgroups
		experiments = []
		for experimentgroup in experimentgroups:
			experiments.append(experimentgroup.experiment)
		return experiments

	def deleteUser(self, id): #CHECK
	#Deletes also dataitems in user
		user = self.dbsession.query(Users).filter_by(id=id).one()
		self.dbsession.delete(user)

	def getDataitemsForUser(self, id): #OK
		return self.dbsession.query(DataItems).filter_by(user_id=id)

	def checkUser(self, data): #OK
		user = self.dbsession.query(Users).filter_by(username=username).one()
		if user == []:
			return self.createUser(data)
		else:
			return user

	#TODO getConfigurationForUser

#---------------------------------------------------------------------------------
#                                    Dataitems                                     
#---------------------------------------------------------------------------------
	
	def createDataitem(self, data): #CHECK
		userId = data['user']
		value = data['value']
		dataitem = DataItems(value=value, user=self.getUser(userId))
		self.dbsession.add(dataitem)
		return dataitem

	#TODO deleteDataitem

#---------------------------------------------------------------------------------
#                                 Configurations                                  
#---------------------------------------------------------------------------------

	def createConfiguration(self, data):
		key = data['key']
		value = data['value']
		experimentgroup = data['experimentgroup']
		configuration = Configurations(key=key, value=value, experimentgroup=experimentgroup)
		self.dbsession.add(configuration)
		return configuration

	#TODO deleteConfiguration

	#TODO getUsersInConfiguration?












