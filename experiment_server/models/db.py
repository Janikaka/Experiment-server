from .experimentGroups import ExperimentGroups
from .experiments import Experiments
from .users import Users
from .dataItems import DataItems

class DatabaseInterface:
	def __init__(self, dbsession):
		self.dbsession = dbsession

#---------------------------------------------------------------------------------
#                                   Experiments                                   
#---------------------------------------------------------------------------------
	def createExperiment(self, data):
		name = data['name']
		experimentgroupNames = data['experimentgroupNames']
		experiment = Experiments(name=name)
		for experimentgroup in experimentgroupNames:
			experimentgroup = ExperimentGroups(name=experimentgroup)
			self.dbsession.add(experimentgroup)
			experiment.experimentgroups.append(experimentgroup)
		self.dbsession.add(experiment)
		return experiment

	def getAllExperiments(self):
		return self.dbsession.query(Experiments).all()

	def getExperiment(self, id):
		return self.dbsession.query(Experiments).filter_by(id=id).one()

	def deleteExperiment(self, id):
		experiment = self.dbsession.query(Experiments).filter_by(id=id).one()
		self.dbsession.delete(experiment)

	def getUsersInExperiment(self, id):
		experimentgroups = self.dbsession.query(Experiments).filter_by(id=id).one().experimentgroups
		users = []
		for experimentgroup in experimentgroups:
			users.extend(experimentgroup.users)
		return users


#---------------------------------------------------------------------------------
#                                      Users                                      
#---------------------------------------------------------------------------------
	def createUser(self, data):
		username = data['username']
		password = data['password']
		if data['experimentgroups'] != None:
			user = Users(username=username, password=password, experimentgroups=data['experimentgroups'])
		else:
			user = Users(username=username, password=password)
		self.dbsession.add(user)
		return user

	def getUser(self, id):
		return self.dbsession.query(Users).filter_by(id=id).one()

	def getAllUsers(self):
		return self.dbsession.query(Users).all()

	def getExperimentsForUser(self, id):
		experimentgroups = self.dbsession.query(Users).filter_by(id=id).one().experimentgroups
		experiments = []
		for experimentgroup in experimentgroups:
			experiments.append(experimentgroup.experiment)
		return experiments

	def deleteUser(self, id):
		user = self.dbsession.query(Users).filter_by(id=id).one()
		self.dbsession.delete(user)

#---------------------------------------------------------------------------------
#                                    Dataitems                                     
#---------------------------------------------------------------------------------
	
	def createDataitem(self, data):
		user = data['user']
		value = data['value']
		dataitem = DataItems(value=value, user=user)
		self.dbsession.add(dataitem)
		return dataitem



