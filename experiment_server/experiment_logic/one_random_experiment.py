import random
from .abstract_experiment_logic import AbstractExperimentLogic
from ..models import (Application, Experiment)


class OneRandomExperiment(AbstractExperimentLogic):
    """
    Logic which returns one Application's random Experiment. This should NOT be called outside ExperimentLogicSelector
    """

    def get_name(self):
        return 'one_random'

    def get_experiments(self, application):
        """
        Returns one random, RUNNING experiment. Fails if none exists
        :param application:
        :return: returns an Experiment if successful, None if none running Experiments exist
        """
        experiments = Experiment.query().join(Application) \
            .filter(Application.id == application.id)

        running_experiments = list(filter(lambda _: _.get_status() == 'running', experiments))

        try:
            return random.choice(running_experiments)
        except IndexError as e:
            self.log_error('Application %s has no running experiments' % application.name)
            return None
