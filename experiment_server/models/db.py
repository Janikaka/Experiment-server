from  .experimentGroups import ExperimentGroups
from .experiments import Experiments

class DatabaseInterface:
	def __init__(self, request):
		self.dbsession = request.dbsession

	def addExperiment(self, name, experimentgroups):
		experiment = Experiments(name=name)
		for experimentgroup in experimentgroups:
			experimentgroup = ExperimentGroups(name=experimentgroup)
			self.dbsession.add(experimentgroup)
			experiment.experimentgroups.append(experimentgroup)
		self.dbsession.add(experiment)

	def getAllExperiments(self):
		return self.dbsession.query(Experiments).all()

	def getExperiment(self, id):
		return self.dbsession.query(Experiments).filter_by(id=id).one()