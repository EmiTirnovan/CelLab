import unittest
from cellab.core.id_generator import IDGenerator
from cellab.core.models import ExperimentParams, CellType
from cellab.world.grid import Position, GridState
from cellab.world.initializer import WorldInitializer

class TestGridAndNeighbors(unittest.TestCase):
    def setUp(self):
        IDGenerator.reset_all()

    def test_position_is_within(self):
        p1 = Position(2, 3)
        self.assertTrue(p1.is_within(5, 5))
        self.assertFalse(p1.is_within(2, 3))

    def test_grid_boundaries_fixed_and_wrap(self):
        # Grilă 3x3 pe mod FIXED
        grid_fixed = GridState(width=3, height=3, boundary_type="FIXED", default_border_state=0)
        grid_fixed.set_cell(0, 0, 5)
        # Acces în afara limitelor pe FIXED trebuie să returneze default_border_state (0)
        self.assertEqual(grid_fixed.get_cell(-1, 0), 0)
        self.assertEqual(grid_fixed.get_cell(5, 5), 0)

        # Grilă 3x3 pe mod WRAP
        grid_wrap = GridState(width=3, height=3, boundary_type="WRAP")
        grid_wrap.set_cell(0, 0, 7)
        # Acces în afara limitelor pe WRAP face modulo (-1 devine indexul 2)
        self.assertEqual(grid_wrap.get_cell(-1, 0), grid_wrap.cells[2][0])

    def test_clone_isolation(self):
        grid = GridState(width=3, height=3)
        grid.set_cell(1, 1, 1)
        clone = grid.clone_for_next_generation()
        
        # Modificarea clonës nu trebuie să afecteze originalul
        clone.set_cell(1, 1, 2)
        self.assertEqual(grid.get_cell(1, 1), 1)
        self.assertEqual(clone.get_cell(1, 1), 2)
        self.assertEqual(clone.generation_index, grid.generation_index + 1)

    def test_neighbors_and_counting(self):
        grid = GridState(width=3, height=3, boundary_type="FIXED")
        # Setăm câteva celule
        grid.set_cell(0, 0, 1)
        grid.set_cell(0, 1, 1)
        
        moore = grid.get_moore_neighbors(0, 0)
        self.assertEqual(grid.count_neighbors_in_state(moore, 1), 1)
        self.assertEqual(grid.count_cells_of_type(1), 2)

    def test_initializer_modes(self):
        params = ExperimentParams(automaton_name="Test", width=3, height=3, num_generations=5, random_seed=42)
        
        # 1. Custom Matrix
        matrix = [[1, 0, 1], [0, 1, 0], [1, 0, 1]]
        g_custom = WorldInitializer.from_custom_matrix(params, matrix)
        self.assertEqual(g_custom.get_cell(0, 0), 1)

        # 2. Center Seed
        g_center = WorldInitializer.from_center_seed(params, seed_state=1)
        self.assertEqual(g_center.get_cell(1, 1), 1)

        # 3. Random Reproducibility
        g_rand1 = WorldInitializer.from_random(params, num_states=2)
        g_rand2 = WorldInitializer.from_random(params, num_states=2)
        self.assertTrue(g_rand1.equals(g_rand2))

    def test_render_ascii(self):
        cell_types = [
            CellType(state_id=0, name="Dead", symbol="."),
            CellType(state_id=1, name="Alive", symbol="1")
        ]
        grid = GridState(width=2, height=2)
        grid.set_cell(0, 1, 1)
        ascii_str = grid.render_ascii(cell_types)
        expected = ".1\n.."
        self.assertEqual(ascii_str, expected)

if __name__ == "__main__":
    unittest.main()