import unittest
from cellab.core.id_generator import IDGenerator
from cellab.core.models import CellType, AutomatonDefinition, ExperimentParams

class TestCoreAndIDs(unittest.TestCase):
    def setUp(self):
        IDGenerator.reset_all()

    def test_id_generator_sequences(self):
        self.assertEqual(IDGenerator.next_id(IDGenerator.CAT_AUTOMATON), 1)
        self.assertEqual(IDGenerator.next_id(IDGenerator.CAT_AUTOMATON), 2)
        self.assertEqual(IDGenerator.next_id(IDGenerator.CAT_GRID_STATE), 1)
        with self.assertRaises(ValueError):
            IDGenerator.next_id(99)

    def test_cell_type_validation(self):
        ct = CellType(state_id=0, name="Dead", symbol=".")
        self.assertTrue(ct.validate())
        with self.assertRaises(ValueError):
            CellType(state_id=0, name="Invalid", symbol="TOOLONG").validate()

    def conf_automaton_duplicates(self):
        defn = AutomatonDefinition(name="Test", dimension=2, neighborhood_type="MOORE")
        defn.add_cell_type("Dead", ".")
        with self.assertRaises(ValueError):
            defn.add_cell_type("AlsoDead", ".")  # Simbol duplicat

    def test_experiment_params_validation(self):
        params = ExperimentParams(automaton_name="Test", width=10, height=10, num_generations=5)
        self.assertTrue(params.validate())
        with self.assertRaises(ValueError):
            ExperimentParams(automaton_name="Test", width=0, height=10, num_generations=5)

if __name__ == "__main__":
    unittest.main()