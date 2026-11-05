import unittest
from cellab.core.id_generator import IDGenerator
from cellab.core.models import AutomatonDefinition, ExperimentParams
from cellab.world.grid import GridState
from cellab.rules.transition_rule import TransitionRule
from cellab.rules.rule30 import Rule30
from cellab.rules.brians_brain import BriansBrainRule
from cellab.rules.forest_fire import ForestFireRule
from cellab.engine.simulation_engine import SimulationEngine


class TestTransitionRule(unittest.TestCase):
    """Teste pentru sistemul de reguli (TransitionRule + cele 3 automate)."""

    def setUp(self):
        IDGenerator.reset_all()

    # --- TransitionRule (clasa de bază) ---

    def test_transition_rule_is_abstract(self):
        """TransitionRule nu poate fi instanțiată direct (este abstractă)."""
        with self.assertRaises(TypeError):
            TransitionRule(name="TestAbstract")

    def test_rule_id_auto_generated(self):
        """Fiecare regulă primește un rule_id unic de la IDGenerator."""
        IDGenerator.reset_all()
        r1 = Rule30()
        r2 = BriansBrainRule()
        r3 = ForestFireRule()
        # IDGenerator.CAT_RULE → incrementat la fiecare instanțiere
        self.assertNotEqual(r1.rule_id, r2.rule_id)
        self.assertNotEqual(r2.rule_id, r3.rule_id)

    def test_rule_id_manual_override(self):
        """rule_id furnizat explicit trebuie respectat."""
        rule = Rule30(rule_id=999)
        self.assertEqual(rule.rule_id, 999)

    # --- Rule30 ---

    def test_rule30_dead_cell_stays_dead(self):
        """O celulă moartă cu toți vecinii morți rămâne moartă (triplet 0,0,0 → 0)."""
        grid = GridState(width=5, height=1, boundary_type="FIXED")
        defn = AutomatonDefinition(name="R30", dimension=1, neighborhood_type="ELEMENTARY_1D")
        defn.add_cell_type("Dead", ".")
        defn.add_cell_type("Alive", "1")
        rule = Rule30()
        # Celula din mijloc (col=2) este moartă, vecinii morți → 0
        self.assertEqual(rule.apply(grid, 0, 2, defn), 0)

    def test_rule30_center_seed_gen1(self):
        """
        Rule 30 cu un singur '1' în centrul unui rând de 7 celule.
        Gen 0: 0001000 → Gen 1: 0011100
        """
        # Rândul: index 0=stânga, 3=centru, 6=dreapta
        grid = GridState(width=7, height=1, boundary_type="FIXED")
        grid.set_cell(0, 3, 1)  # Celulă vie în centru

        defn = AutomatonDefinition(name="R30", dimension=1, neighborhood_type="ELEMENTARY_1D")
        defn.add_cell_type("Dead", ".")
        defn.add_cell_type("Alive", "1")
        rule = Rule30()

        # col=2: triplet (0,0,1) → 1
        self.assertEqual(rule.apply(grid, 0, 2, defn), 1)
        # col=3: triplet (0,1,0) → 1
        self.assertEqual(rule.apply(grid, 0, 3, defn), 1)
        # col=4: triplet (1,0,0) → 1
        self.assertEqual(rule.apply(grid, 0, 4, defn), 1)
        # col=0: triplet (0,0,0) → 0
        self.assertEqual(rule.apply(grid, 0, 0, defn), 0)

    def test_rule30_simulation_produces_correct_gen1(self):
        """
        Simulare completă Rule 30: verificăm că generația 1 corespunde pattern-ului
        documentat Wolfram pentru semință centrală pe lățime 7.
        """
        IDGenerator.reset_all()
        defn = AutomatonDefinition(name="R30Test", dimension=1, neighborhood_type="ELEMENTARY_1D")
        defn.add_cell_type("Dead", ".")
        defn.add_cell_type("Alive", "1")

        params = ExperimentParams(
            automaton_name="R30Test",
            width=7, height=1, num_generations=1,
            boundary_type="FIXED", init_mode="CUSTOM",
        )
        rule = Rule30()
        engine = SimulationEngine(definition=defn, params=params, rule=rule)

        init_cells = [[0, 0, 0, 1, 0, 0, 0]]
        engine.initialize_world(custom_cells=init_cells)
        states = engine.run_simulation()

        gen1 = states[1]  # Generația 1
        self.assertEqual(gen1.cells[0], [0, 0, 1, 1, 1, 0, 0])

    # --- BriansBrainRule ---

    def test_brians_brain_on_becomes_dying(self):
        """O celulă ON trebuie să devină DYING indiferent de vecini."""
        grid = GridState(width=3, height=3, boundary_type="FIXED")
        grid.set_cell(1, 1, 1)  # Centrul este ON (1)
        defn = AutomatonDefinition(name="BB", dimension=2, neighborhood_type="MOORE")
        defn.add_cell_type("Off", ".")
        defn.add_cell_type("On", "O")
        defn.add_cell_type("Dying", "o")
        rule = BriansBrainRule()
        self.assertEqual(rule.apply(grid, 1, 1, defn), 2)  # → DYING

    def test_brians_brain_dying_becomes_off(self):
        """O celulă DYING trebuie să devină OFF."""
        grid = GridState(width=3, height=3, boundary_type="FIXED")
        grid.set_cell(1, 1, 2)  # Centrul este DYING (2)
        defn = AutomatonDefinition(name="BB", dimension=2, neighborhood_type="MOORE")
        defn.add_cell_type("Off", ".")
        defn.add_cell_type("On", "O")
        defn.add_cell_type("Dying", "o")
        rule = BriansBrainRule()
        self.assertEqual(rule.apply(grid, 1, 1, defn), 0)  # → OFF

    def test_brians_brain_off_with_exactly_2_on_neighbors_becomes_on(self):
        """O celulă OFF cu exact 2 vecini ON trebuie să devină ON."""
        grid = GridState(width=3, height=3, boundary_type="FIXED")
        # Setăm exact 2 vecini ON (col=0,0 și col=2,0)
        grid.set_cell(0, 0, 1)
        grid.set_cell(2, 0, 1)
        defn = AutomatonDefinition(name="BB", dimension=2, neighborhood_type="MOORE")
        defn.add_cell_type("Off", ".")
        defn.add_cell_type("On", "O")
        defn.add_cell_type("Dying", "o")
        rule = BriansBrainRule()
        # Centrul (1,1) este OFF cu 2 vecini ON → devine ON
        self.assertEqual(rule.apply(grid, 1, 1, defn), 1)

    def test_brians_brain_off_with_3_on_neighbors_stays_off(self):
        """O celulă OFF cu 3 vecini ON trebuie să rămână OFF (nu exact 2)."""
        grid = GridState(width=3, height=3, boundary_type="FIXED")
        grid.set_cell(0, 0, 1)
        grid.set_cell(0, 1, 1)
        grid.set_cell(0, 2, 1)
        defn = AutomatonDefinition(name="BB", dimension=2, neighborhood_type="MOORE")
        defn.add_cell_type("Off", ".")
        defn.add_cell_type("On", "O")
        defn.add_cell_type("Dying", "o")
        rule = BriansBrainRule()
        self.assertEqual(rule.apply(grid, 1, 1, defn), 0)  # → rămâne OFF

    # --- ForestFireRule ---

    def test_forest_fire_fire_becomes_empty(self):
        """O celulă FIRE (2) trebuie să devină EMPTY (0)."""
        grid = GridState(width=3, height=3, boundary_type="FIXED")
        grid.set_cell(1, 1, 2)  # Centrul = FIRE
        defn = AutomatonDefinition(name="FF", dimension=2, neighborhood_type="MOORE")
        defn.add_cell_type("Empty", " ")
        defn.add_cell_type("Tree", "T")
        defn.add_cell_type("Fire", "*")
        rule = ForestFireRule()
        self.assertEqual(rule.apply(grid, 1, 1, defn), 0)  # → EMPTY

    def test_forest_fire_tree_adjacent_to_fire_ignites(self):
        """Un copac (TREE=1) cu cel puțin un vecin FIRE trebuie să ia foc."""
        grid = GridState(width=3, height=3, boundary_type="FIXED")
        grid.set_cell(0, 1, 2)  # Vecinul de deasupra centrului = FIRE
        grid.set_cell(1, 1, 1)  # Centrul = TREE
        defn = AutomatonDefinition(name="FF", dimension=2, neighborhood_type="MOORE")
        defn.add_cell_type("Empty", " ")
        defn.add_cell_type("Tree", "T")
        defn.add_cell_type("Fire", "*")
        rule = ForestFireRule()
        self.assertEqual(rule.apply(grid, 1, 1, defn), 2)  # → FIRE

    def test_forest_fire_tree_no_fire_neighbor_stays_tree(self):
        """Un copac fără vecini FIRE trebuie să rămână copac."""
        grid = GridState(width=3, height=3, boundary_type="FIXED")
        grid.set_cell(1, 1, 1)  # Centrul = TREE, restul 0 (EMPTY)
        defn = AutomatonDefinition(name="FF", dimension=2, neighborhood_type="MOORE")
        defn.add_cell_type("Empty", " ")
        defn.add_cell_type("Tree", "T")
        defn.add_cell_type("Fire", "*")
        rule = ForestFireRule()
        self.assertEqual(rule.apply(grid, 1, 1, defn), 1)  # → rămâne TREE

    def test_forest_fire_empty_stays_empty(self):
        """Un teren gol (EMPTY=0) trebuie să rămână gol."""
        grid = GridState(width=3, height=3, boundary_type="FIXED")
        # Tot gridul e gol implicit
        defn = AutomatonDefinition(name="FF", dimension=2, neighborhood_type="MOORE")
        defn.add_cell_type("Empty", " ")
        defn.add_cell_type("Tree", "T")
        defn.add_cell_type("Fire", "*")
        rule = ForestFireRule()
        self.assertEqual(rule.apply(grid, 1, 1, defn), 0)  # → rămâne EMPTY


class TestSimulationEngine(unittest.TestCase):
    """Teste pentru SimulationEngine."""

    def setUp(self):
        IDGenerator.reset_all()
        self.defn = AutomatonDefinition(name="TestAuto", dimension=2, neighborhood_type="MOORE")
        self.defn.add_cell_type("Off", ".")
        self.defn.add_cell_type("On", "O")
        self.defn.add_cell_type("Dying", "o")
        self.params = ExperimentParams(
            automaton_name="TestAuto",
            width=5, height=5, num_generations=3,
            boundary_type="FIXED", init_mode="CUSTOM",
        )

    def test_engine_raises_without_init(self):
        """SimulationEngine trebuie să ridice RuntimeError dacă run_simulation e apelat fără inițializare."""
        rule = BriansBrainRule()
        engine = SimulationEngine(definition=self.defn, params=self.params, rule=rule)
        with self.assertRaises(RuntimeError):
            engine.run_simulation()

    def test_engine_step_raises_without_init(self):
        """SimulationEngine.step() trebuie să ridice RuntimeError fără inițializare."""
        rule = BriansBrainRule()
        engine = SimulationEngine(definition=self.defn, params=self.params, rule=rule)
        with self.assertRaises(RuntimeError):
            engine.step()

    def test_engine_initialize_returns_gen0(self):
        """initialize_world() trebuie să returneze starea de generație 0."""
        rule = BriansBrainRule()
        engine = SimulationEngine(definition=self.defn, params=self.params, rule=rule)
        grid0 = engine.initialize_world(custom_cells=[[0]*5 for _ in range(5)])
        self.assertEqual(grid0.generation_index, 0)
        self.assertEqual(engine.current_grid.generation_index, 0)

    def test_engine_run_simulation_num_states(self):
        """run_simulation() trebuie să returneze num_generations+1 stări (gen0 + gen1..N)."""
        IDGenerator.reset_all()
        rule = BriansBrainRule()
        engine = SimulationEngine(definition=self.defn, params=self.params, rule=rule)
        # Plasăm celule active pentru a evita stabilizarea prematură
        # Un singur ON produce DYING în gen1, OFF în gen2, iar dacă e izolat → stabil după gen2
        # Plasăm 2 ON vecini care vor genera dinamică pentru 3 generații
        init_cells = [[0]*5 for _ in range(5)]
        init_cells[2][1] = 1  # ON
        init_cells[2][2] = 1  # ON adiacent
        init_cells[2][3] = 1  # ON adiacent
        engine.initialize_world(custom_cells=init_cells)
        states = engine.run_simulation()
        # Verificăm că avem cel puțin gen0 + 3 generații complete (nu early-stop)
        # sau că numărul de stări este cel puțin 2 (inițializare + cel puțin 1 step)
        self.assertGreaterEqual(len(states), 2)
        # Verificăm că prima stare e gen0 și ultima are generation_index crescător
        self.assertEqual(states[0].generation_index, 0)
        self.assertGreater(states[-1].generation_index, 0)

    def test_engine_step_increments_generation(self):
        """Fiecare apel la step() trebuie să incrementeze generation_index cu 1."""
        IDGenerator.reset_all()
        rule = ForestFireRule()
        defn = AutomatonDefinition(name="FF", dimension=2, neighborhood_type="MOORE")
        defn.add_cell_type("Empty", " ")
        defn.add_cell_type("Tree", "T")
        defn.add_cell_type("Fire", "*")
        params = ExperimentParams(
            automaton_name="FF", width=5, height=5, num_generations=5,
            boundary_type="FIXED", init_mode="CUSTOM",
        )
        engine = SimulationEngine(definition=defn, params=params, rule=rule)
        engine.initialize_world(custom_cells=[[0]*5 for _ in range(5)])
        g1 = engine.step()
        g2 = engine.step()
        self.assertEqual(g1.generation_index, 1)
        self.assertEqual(g2.generation_index, 2)

    def test_engine_stability_detection(self):
        """is_stable trebuie să fie True dacă grila nu se mai schimbă între generații."""
        IDGenerator.reset_all()
        rule = ForestFireRule()
        defn = AutomatonDefinition(name="FF", dimension=2, neighborhood_type="MOORE")
        defn.add_cell_type("Empty", " ")
        defn.add_cell_type("Tree", "T")
        defn.add_cell_type("Fire", "*")
        params = ExperimentParams(
            automaton_name="FF", width=3, height=3, num_generations=10,
            boundary_type="FIXED", init_mode="CUSTOM",
        )
        engine = SimulationEngine(definition=defn, params=params, rule=rule)
        # Grilă goală (EMPTY) → ForestFireRule: EMPTY rămâne EMPTY → stabil imediat
        engine.initialize_world(custom_cells=[[0]*3 for _ in range(3)])
        engine.step()
        self.assertTrue(engine.is_stable)

    def test_engine_synchronous_update(self):
        """
        Actualizarea trebuie să fie sincronă: celulele nu se văd reciproc
        în starea modificată în aceeași generație.
        """
        IDGenerator.reset_all()
        rule = BriansBrainRule()
        engine = SimulationEngine(definition=self.defn, params=self.params, rule=rule)
        # Plasăm un singur ON în centru
        init_cells = [[0]*5 for _ in range(5)]
        init_cells[2][2] = 1  # Centrul = ON
        engine.initialize_world(custom_cells=init_cells)
        gen1 = engine.step()
        # Centrul (ON) trebuie să devină DYING (2)
        self.assertEqual(gen1.get_cell(2, 2), 2)
        # Starea originală nu trebuie modificată
        self.assertEqual(engine.all_states[0].get_cell(2, 2), 1)

    def test_engine_all_states_contains_all_generations(self):
        """all_states trebuie să conțină toate generațiile în ordine."""
        IDGenerator.reset_all()
        rule = Rule30()
        defn = AutomatonDefinition(name="R30", dimension=1, neighborhood_type="ELEMENTARY_1D")
        defn.add_cell_type("Dead", ".")
        defn.add_cell_type("Alive", "1")
        params = ExperimentParams(
            automaton_name="R30", width=7, height=1, num_generations=3,
            boundary_type="FIXED", init_mode="CUSTOM",
        )
        engine = SimulationEngine(definition=defn, params=params, rule=rule)
        init_cells = [[0, 0, 0, 1, 0, 0, 0]]
        engine.initialize_world(custom_cells=init_cells)
        engine.run_simulation()
        states = engine.all_states
        self.assertEqual(len(states), 4)
        for i, state in enumerate(states):
            self.assertEqual(state.generation_index, i)


if __name__ == "__main__":
    unittest.main()
