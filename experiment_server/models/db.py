from .experimentGroups import ExperimentGroups
from .experiments import Experiments
from .users import Users

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

	def getAllExperiments(self):
		return self.dbsession.query(Experiments).all()

	def getExperiment(self, id):
		return self.dbsession.query(Experiments).filter_by(id=id).one()

	def deleteExperiment(self, id):
		experiment = self.dbsession.query(Experiments).filter_by(id=id).one()
		self.dbsession.delete(experiment)

#---------------------------------------------------------------------------------
#                                      Users                                      
#---------------------------------------------------------------------------------
	def createUser(self, data):
		username = data['username']
		password = data['password']
		user = Users(username=username, password=password)
		self.dbsession.add(user)

	def getAllUsers(self):
		return self.dbsession.query(Users).all()
