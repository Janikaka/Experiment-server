from .abstract_experiment_logic import AbstractExperimentLogic
from .one_random_experiment import OneRandomExperiment


class ExperimentLogicSelector(AbstractExperimentLogic):
    """
    Logic, which returns Experiments assigned by Application's experiment_distribution. ONLY THIS CLASS should be
    imported outside experiment_logic-package.
    """
    def __init__(self):
        """
        Remember to add new ExperimentLogics to logics attribute! Default logic is assigned to default.
        """
        random = OneRandomExperiment()
        self.logics = {random.get_name(): random.get_experiments}
        self.default = random.get_experiments

    def get_name(self):
        return 'logic_selector'

    def get_experiments(self, application):
        """
        If Application does not have a valid experiment_distribution, the selector returns the default ExperimentLogic.
        :param application:
        :return: Either Logic named by Application's experiment_distribution or the default Logic
        """
        logic_name = application.experiment_distribution

        try:
            logic = self.logics[logic_name]
            return logic(application)
        except KeyError:
            self.log_error('Application %s does not have a valid experiment_distribution. '
                           'Returning Experiments with default Experiment Logic' % application.name)
            return self.default(application)

    def get_valid_experiment_logics(self):
        """
        Return all current experiment distributin strategies.
        :return: Names of valid ExperimentLogics
        """
        return self.logics.keys()

    def is_valid_experiment_logic(self, logic_name):
        """
        Checks if given logic_name is valid ExperimentLogic
        :param logic_name:
        :return: True: such logic exists, False: given logic_name is invalid
        """
        return logic_name in self.logics.keys()
