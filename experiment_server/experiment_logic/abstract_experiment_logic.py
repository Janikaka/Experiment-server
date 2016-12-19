import abc
import datetime
import logging


class AbstractExperimentLogic(object):
    """
    Abstract class for ExperimentLogic. This should not be imported outside ExperimentLogics
    """
    __metaclass__ = abc.ABCMeta
    log = logging.getLogger(__name__)

    def log_error(self, message):
        """
        Logs an error, if encountered.
        :param message: message to be printed
        """
        self.log.debug("%s %s %s" % (datetime.datetime.now(), self.get_name(), message))

    @abc.abstractmethod
    def get_name(self):
        """
        Returns the name of the ExperimentLogic
        :return: returns ExperimentLogic's name as String
        """
        return

    @abc.abstractmethod
    def get_experiments(self, application):
        """
        Returns Experiment(s)
        :param application: Applications where experiments are fetched from
        :return: One or more Experiments depending on ExperimentLogic
        """
        return
