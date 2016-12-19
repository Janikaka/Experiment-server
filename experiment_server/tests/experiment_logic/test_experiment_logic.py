from ..base_test import BaseTest
from experiment_server.models.applications import Application
from experiment_server.experiment_logic.experiment_logic_selector import ExperimentLogicSelector
from experiment_server.experiment_logic.one_random_experiment import OneRandomExperiment


class TestExperimentLogic(BaseTest):

    def setUp(self):
        super(TestExperimentLogic, self).setUp()
        self.init_database()
        self.init_databaseData()

    def test_name_is_not_none(self):
        test_logic = ExperimentLogicSelector()

        assert test_logic.get_name() is not None

    def test_returns_one_random_experiment(self):
        app = Application.get(1)
        one_random = OneRandomExperiment()

        assert one_random.get_experiments(app) in app.experiments

    def test_returns_none_if_no_running_experiments(self):
        app = Application(name='Aperture science')
        one_random = OneRandomExperiment()

        assert one_random.get_experiments(app) is None

    def test_selector_returns_one_random_if_set_on_application(self):
        app = Application.get(1)
        app.experiment_distribution = OneRandomExperiment().get_name()

        logic_selector = ExperimentLogicSelector()

        assert logic_selector.get_experiments(app) in app.experiments

    def test_selector_returns_one_random_if_experimentditribution_not_set(self):
        app = Application.get(1)

        logic_selector = ExperimentLogicSelector()

        assert logic_selector.get_experiments(app) in app.experiments

