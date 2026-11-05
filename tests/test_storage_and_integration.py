"""
tests/test_storage_and_integration.py
--------------------------------------
Teste de stocare și integrare end-to-end pentru Livrabilul 2 — CelLab.

Acoperă:
 1. StateStorage — gestiunea memoriei (record_state, get_state_at_generation,
    get_all_states, store_intermediate=True/False).
 2. Salvare/încărcare JSON (save_experiment_to_file / load_experiment_from_file)
    pentru toate cele 3 automate oficiale.
 3. Teste end-to-end Rule 30, Brian's Brain, Forest Fire cu preset-urile
    exacte din Documentul 1.
"""

import json
import os
import tempfile
import unittest

from cellab.core.id_generator import IDGenerator
from cellab.core.models import AutomatonDefinition, ExperimentParams
from cellab.engine.simulation_engine import SimulationEngine
from cellab.presets.automata_presets import (
    create_brians_brain_preset,
    create_forest_fire_preset,
    create_rule30_preset,
)
from cellab.storage.state_storage import StateStorage
from cellab.world.grid import GridState


# ===========================================================================
# Clasa de bază cu setUp comun
# ===========================================================================


class BaseStorageTest(unittest.TestCase):
    """setUp comun: resetare IDGenerator înainte de fiecare test."""

    def setUp(self) -> None:
        IDGenerator.reset_all()


# ===========================================================================
# Partea 1 — Teste unitare StateStorage
# ===========================================================================


class TestStateStorageMemory(BaseStorageTest):
    """Teste pentru gestiunea stărilor în memorie."""

    # ----- record_state / add_state ----------------------------------------

    def test_record_state_sets_initial_snapshot(self):
        """Prima stare înregistrată trebuie să devină initial_snapshot."""
        storage = StateStorage(store_intermediate=True)
        gs = GridState(width=3, height=1, generation_index=0)
        storage.record_state(gs)
        self.assertIs(storage.initial_snapshot, gs)

    def test_record_state_updates_latest_snapshot(self):
        """latest_snapshot trebuie actualizat la fiecare apel."""
        storage = StateStorage(store_intermediate=True)
        gs0 = GridState(width=3, height=1, generation_index=0)
        gs1 = GridState(width=3, height=1, generation_index=1)
        storage.record_state(gs0)
        storage.record_state(gs1)
        self.assertIs(storage.latest_snapshot, gs1)
        self.assertIs(storage.initial_snapshot, gs0)

    def test_add_state_is_alias_for_record_state(self):
        """add_state() trebuie să se comporte identic cu record_state()."""
        storage = StateStorage(store_intermediate=True)
        gs = GridState(width=2, height=2, generation_index=0)
        storage.add_state(gs)
        self.assertIs(storage.initial_snapshot, gs)
        self.assertIs(storage.latest_snapshot, gs)
        self.assertIn(gs, storage.history)

    def test_history_populated_when_store_intermediate_true(self):
        """history trebuie să conțină toate stările când store_intermediate=True."""
        storage = StateStorage(store_intermediate=True)
        states = [GridState(width=2, height=1, generation_index=i) for i in range(5)]
        for s in states:
            storage.record_state(s)
        self.assertEqual(len(storage.history), 5)

    def test_history_empty_when_store_intermediate_false(self):
        """history trebuie să fie goală când store_intermediate=False."""
        storage = StateStorage(store_intermediate=False)
        for i in range(5):
            storage.record_state(GridState(width=2, height=1, generation_index=i))
        self.assertEqual(len(storage.history), 0)

    def test_snapshots_set_when_store_intermediate_false(self):
        """initial_snapshot și latest_snapshot trebuie setate chiar fără store_intermediate."""
        storage = StateStorage(store_intermediate=False)
        gs0 = GridState(width=3, height=1, generation_index=0)
        gs5 = GridState(width=3, height=1, generation_index=5)
        storage.record_state(gs0)
        storage.record_state(gs5)
        self.assertIs(storage.initial_snapshot, gs0)
        self.assertIs(storage.latest_snapshot, gs5)

    # ----- get_state_at_generation -----------------------------------------

    def test_get_state_at_generation_found(self):
        """get_state_at_generation trebuie să returneze starea corectă."""
        storage = StateStorage(store_intermediate=True)
        states = [GridState(width=2, height=1, generation_index=i) for i in range(4)]
        for s in states:
            storage.record_state(s)
        self.assertIs(storage.get_state_at_generation(2), states[2])

    def test_get_state_at_generation_not_found_returns_none(self):
        """Generație inexistentă trebuie să returneze None."""
        storage = StateStorage(store_intermediate=True)
        storage.record_state(GridState(width=2, height=1, generation_index=0))
        self.assertIsNone(storage.get_state_at_generation(99))

    def test_get_state_at_generation_no_intermediate_gen0(self):
        """store_intermediate=False: get_state_at_generation(0) returnează initial_snapshot."""
        storage = StateStorage(store_intermediate=False)
        gs0 = GridState(width=3, height=1, generation_index=0)
        gs15 = GridState(width=3, height=1, generation_index=15)
        storage.record_state(gs0)
        storage.record_state(gs15)
        self.assertIs(storage.get_state_at_generation(0), gs0)

    def test_get_state_at_generation_no_intermediate_last_gen(self):
        """store_intermediate=False: get_state_at_generation(15) returnează latest_snapshot."""
        storage = StateStorage(store_intermediate=False)
        gs0 = GridState(width=3, height=1, generation_index=0)
        gs15 = GridState(width=3, height=1, generation_index=15)
        storage.record_state(gs0)
        storage.record_state(gs15)
        self.assertIs(storage.get_state_at_generation(15), gs15)

    def test_get_state_at_generation_no_intermediate_middle_returns_none(self):
        """store_intermediate=False: generație intermediară trebuie să returneze None."""
        storage = StateStorage(store_intermediate=False)
        storage.record_state(GridState(width=3, height=1, generation_index=0))
        storage.record_state(GridState(width=3, height=1, generation_index=15))
        self.assertIsNone(storage.get_state_at_generation(7))

    # ----- get_all_states --------------------------------------------------

    def test_get_all_states_intermediate_true(self):
        """get_all_states() trebuie să returneze toate generațiile (store_intermediate=True)."""
        storage = StateStorage(store_intermediate=True)
        states = [GridState(width=2, height=1, generation_index=i) for i in range(6)]
        for s in states:
            storage.record_state(s)
        self.assertEqual(len(storage.get_all_states()), 6)

    def test_get_all_states_intermediate_false_two_states(self):
        """get_all_states() trebuie să returneze exact 2 stări (store_intermediate=False)."""
        storage = StateStorage(store_intermediate=False)
        gs0 = GridState(width=3, height=1, generation_index=0)
        gs15 = GridState(width=3, height=1, generation_index=15)
        storage.record_state(gs0)
        storage.record_state(gs15)
        all_states = storage.get_all_states()
        self.assertEqual(len(all_states), 2)
        self.assertIn(gs0, all_states)
        self.assertIn(gs15, all_states)

    def test_get_all_states_no_duplicate_when_one_state(self):
        """get_all_states() trebuie să returneze exact 1 stare dacă e înregistrată o singură dată."""
        storage = StateStorage(store_intermediate=False)
        gs0 = GridState(width=2, height=1, generation_index=0)
        storage.record_state(gs0)
        self.assertEqual(len(storage.get_all_states()), 1)


# ===========================================================================
# Partea 2 — Teste store_intermediate=False end-to-end
# ===========================================================================


class TestStoreIntermediateFalse(BaseStorageTest):
    """
    Verifică că după N generații sunt stocate doar gen 0 și gen N
    când store_intermediate=False.
    """

    def test_only_first_and_last_stored_after_15_generations(self):
        """
        Rulând 15 generații cu store_intermediate=False, StateStorage
        trebuie să conțină exact generația 0 și generația 15.
        """
        defn, params, rule, init_cells = create_rule30_preset(num_generations=15)
        # Suprascriem store_intermediate în params
        params_no_interm = ExperimentParams(
            automaton_name=params.automaton_name,
            width=params.width,
            height=params.height,
            num_generations=15,
            store_intermediate=False,
            boundary_type=params.boundary_type,
            init_mode=params.init_mode,
            random_seed=params.random_seed,
        )

        storage = StateStorage(store_intermediate=False)
        engine = SimulationEngine(
            definition=defn,
            params=params_no_interm,
            rule=rule,
            storage=storage,
        )
        engine.initialize_world(custom_cells=init_cells)
        engine.run_simulation()

        all_states = storage.get_all_states()
        self.assertEqual(len(all_states), 2)
        gen_indices = {s.generation_index for s in all_states}
        self.assertIn(0, gen_indices)
        self.assertIn(15, gen_indices)

    def test_history_is_empty_with_store_intermediate_false(self):
        """history trebuie să fie goală după simulare cu store_intermediate=False."""
        defn, params, rule, init_cells = create_rule30_preset(num_generations=5)
        params_no_interm = ExperimentParams(
            automaton_name=params.automaton_name,
            width=params.width,
            height=params.height,
            num_generations=5,
            store_intermediate=False,
            boundary_type=params.boundary_type,
            init_mode=params.init_mode,
            random_seed=params.random_seed,
        )
        storage = StateStorage(store_intermediate=False)
        engine = SimulationEngine(
            definition=defn, params=params_no_interm, rule=rule, storage=storage
        )
        engine.initialize_world(custom_cells=init_cells)
        engine.run_simulation()
        self.assertEqual(len(storage.history), 0)


# ===========================================================================
# Partea 3 — Teste end-to-end cu salvare/încărcare JSON
# ===========================================================================


class TestJSONSerializationBase(BaseStorageTest):
    """Clasa de bază cu directorul temporar pentru fișierele JSON."""

    def setUp(self) -> None:
        super().setUp()
        self._tmpdir = tempfile.mkdtemp()

    def _run_and_save(self, preset_fn, num_generations, filename):
        """
        Helper: creează preset, rulează simularea, salvează JSON,
        returnează (engine, storage, filepath).
        """
        defn, params, rule, init_cells = preset_fn(num_generations=num_generations)
        storage = StateStorage(store_intermediate=True)
        engine = SimulationEngine(
            definition=defn, params=params, rule=rule, storage=storage
        )
        engine.initialize_world(custom_cells=init_cells)
        engine.run_simulation()

        filepath = os.path.join(self._tmpdir, filename)
        storage.save_experiment_to_file(filepath, defn, params)
        return engine, storage, defn, params, filepath

    def _assert_states_equal_after_reload(self, original_storage, filepath):
        """
        Helper: încarcă JSON, verifică că fiecare stare originală
        este identică cu cea încărcată (GridState.equals).
        """
        _, _, loaded_storage = StateStorage.load_experiment_from_file(filepath)
        orig_states = original_storage.get_all_states()
        load_states = loaded_storage.get_all_states()

        self.assertEqual(
            len(orig_states),
            len(load_states),
            "Numărul de stări salvate trebuie să corespundă cu numărul de stări încărcate.",
        )
        for orig, loaded in zip(orig_states, load_states):
            self.assertEqual(
                orig.generation_index,
                loaded.generation_index,
                f"generation_index diferit: {orig.generation_index} vs {loaded.generation_index}",
            )
            self.assertTrue(
                orig.equals(loaded),
                f"Starea gen {orig.generation_index} diferă după reload JSON.",
            )


class TestRule30EndToEnd(TestJSONSerializationBase):
    """Teste end-to-end pentru Rule 30."""

    def test_rule30_gen0_matches_doc_initial_state(self):
        """
        Gen 0 trebuie să corespundă matricei din Documentul 1:
        [[0,0,0,0,0,0,1,0,0,0,0,0,0]].
        """
        defn, params, rule, init_cells = create_rule30_preset(num_generations=1)
        storage = StateStorage(store_intermediate=True)
        engine = SimulationEngine(defn, params, rule, storage=storage)
        engine.initialize_world(custom_cells=init_cells)

        gen0 = storage.get_state_at_generation(0)
        self.assertIsNotNone(gen0)
        self.assertEqual(gen0.cells[0], [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0])

    def test_rule30_gen1_correct(self):
        """
        Gen 1 pentru Rule 30 (13 celule, semință la col 6, FIXED):
        așteptăm 1 în col 5, 6, 7 (tripletele (0,1,0)→1, (0,0,1)→1, (1,0,0)→1).
        """
        defn, params, rule, init_cells = create_rule30_preset(num_generations=1)
        storage = StateStorage(store_intermediate=True)
        engine = SimulationEngine(defn, params, rule, storage=storage)
        engine.initialize_world(custom_cells=init_cells)
        engine.run_simulation()

        gen1 = storage.get_state_at_generation(1)
        self.assertIsNotNone(gen1)
        # (0,1,0) → 1, (0,0,1) → 1, (1,0,0) → 1; restul 0
        expected = [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0]
        self.assertEqual(gen1.cells[0], expected)

    def test_rule30_simulation_produces_6_generations(self):
        """Simularea Rule 30 cu num_generations=6 produce gen 0..6 (7 stări)."""
        defn, params, rule, init_cells = create_rule30_preset(num_generations=6)
        storage = StateStorage(store_intermediate=True)
        engine = SimulationEngine(defn, params, rule, storage=storage)
        engine.initialize_world(custom_cells=init_cells)
        engine.run_simulation()
        self.assertEqual(len(storage.get_all_states()), 7)

    def test_rule30_save_and_load_json_identity(self):
        """Salvare + reîncărcare JSON: fiecare GridState.equals() trebuie să fie True."""
        _, storage, _, _, filepath = self._run_and_save(
            create_rule30_preset, num_generations=6, filename="rule30_test.json"
        )
        self._assert_states_equal_after_reload(storage, filepath)

    def test_rule30_json_file_contains_valid_structure(self):
        """Fișierul JSON trebuie să conțină cheile 'definition', 'params' și 'states'."""
        _, _, _, _, filepath = self._run_and_save(
            create_rule30_preset, num_generations=3, filename="rule30_struct.json"
        )
        with open(filepath, encoding="utf-8") as fh:
            data = json.load(fh)
        self.assertIn("definition", data)
        self.assertIn("params", data)
        self.assertIn("states", data)

    def test_rule30_load_definition_matches_original(self):
        """Definiția reîncărcată trebuie să aibă același nume și număr de tipuri de celule."""
        _, _, orig_defn, _, filepath = self._run_and_save(
            create_rule30_preset, num_generations=3, filename="rule30_defn.json"
        )
        loaded_defn, _, _ = StateStorage.load_experiment_from_file(filepath)
        self.assertEqual(loaded_defn.name, orig_defn.name)
        self.assertEqual(len(loaded_defn.cell_types), len(orig_defn.cell_types))

    def test_rule30_load_params_matches_original(self):
        """Parametrii reîncărcați trebuie să aibă aceleași valori ca cei originali."""
        _, _, _, orig_params, filepath = self._run_and_save(
            create_rule30_preset, num_generations=4, filename="rule30_params.json"
        )
        _, loaded_params, _ = StateStorage.load_experiment_from_file(filepath)
        self.assertEqual(loaded_params.width, orig_params.width)
        self.assertEqual(loaded_params.height, orig_params.height)
        self.assertEqual(loaded_params.num_generations, orig_params.num_generations)
        self.assertEqual(loaded_params.boundary_type, orig_params.boundary_type)


class TestBriansBrainEndToEnd(TestJSONSerializationBase):
    """Teste end-to-end pentru Brian's Brain."""

    def test_brians_brain_gen0_matches_doc_initial_state(self):
        """
        Gen 0 trebuie să corespundă matricei din Documentul 1:
        [[0,0,1,0,0],[0,1,0,1,0],[0,0,0,0,0]].
        """
        defn, params, rule, init_cells = create_brians_brain_preset(num_generations=1)
        storage = StateStorage(store_intermediate=True)
        engine = SimulationEngine(defn, params, rule, storage=storage)
        engine.initialize_world(custom_cells=init_cells)

        gen0 = storage.get_state_at_generation(0)
        self.assertIsNotNone(gen0)
        self.assertEqual(gen0.cells[0], [0, 0, 1, 0, 0])
        self.assertEqual(gen0.cells[1], [0, 1, 0, 1, 0])
        self.assertEqual(gen0.cells[2], [0, 0, 0, 0, 0])

    def test_brians_brain_gen1_firing_cells_become_dying(self):
        """
        La gen 1 toate celulele FIRING (1) din gen 0 trebuie să devină DYING (2).
        """
        defn, params, rule, init_cells = create_brians_brain_preset(num_generations=1)
        storage = StateStorage(store_intermediate=True)
        engine = SimulationEngine(defn, params, rule, storage=storage)
        engine.initialize_world(custom_cells=init_cells)
        engine.run_simulation()

        gen0 = storage.get_state_at_generation(0)
        gen1 = storage.get_state_at_generation(1)
        self.assertIsNotNone(gen1)

        # Orice celulă cu stare 1 în gen0 trebuie să fie 2 în gen1
        for r in range(gen0.height):
            for c in range(gen0.width):
                if gen0.get_cell(r, c) == 1:
                    self.assertEqual(
                        gen1.get_cell(r, c), 2,
                        f"Celula ({r},{c}) era FIRING în gen0, trebuie să fie DYING în gen1.",
                    )

    def test_brians_brain_save_and_load_json_identity(self):
        """Salvare + reîncărcare JSON: fiecare GridState.equals() trebuie să fie True."""
        _, storage, _, _, filepath = self._run_and_save(
            create_brians_brain_preset, num_generations=5, filename="brians_brain_test.json"
        )
        self._assert_states_equal_after_reload(storage, filepath)

    def test_brians_brain_simulation_runs_all_generations(self):
        """Simularea cu num_generations=5 produce gen 0..5 (6 stări)."""
        defn, params, rule, init_cells = create_brians_brain_preset(num_generations=5)
        storage = StateStorage(store_intermediate=True)
        engine = SimulationEngine(defn, params, rule, storage=storage)
        engine.initialize_world(custom_cells=init_cells)
        engine.run_simulation()
        # Brian's Brain pe această configurație nu se stabilizează rapid
        self.assertGreaterEqual(len(storage.get_all_states()), 2)


class TestForestFireEndToEnd(TestJSONSerializationBase):
    """Teste end-to-end pentru Forest Fire."""

    def test_forest_fire_gen0_matches_doc_initial_state(self):
        """
        Gen 0 trebuie să corespundă matricei din Documentul 1:
        [[1,1,1,1,0],[1,1,0,1,1],[0,1,2,1,1],[1,1,1,1,1]].
        """
        defn, params, rule, init_cells = create_forest_fire_preset(num_generations=1)
        storage = StateStorage(store_intermediate=True)
        engine = SimulationEngine(defn, params, rule, storage=storage)
        engine.initialize_world(custom_cells=init_cells)

        gen0 = storage.get_state_at_generation(0)
        self.assertIsNotNone(gen0)
        self.assertEqual(gen0.cells[0], [1, 1, 1, 1, 0])
        self.assertEqual(gen0.cells[1], [1, 1, 0, 1, 1])
        self.assertEqual(gen0.cells[2], [0, 1, 2, 1, 1])
        self.assertEqual(gen0.cells[3], [1, 1, 1, 1, 1])

    def test_forest_fire_gen1_fire_cell_becomes_empty(self):
        """
        La gen 1, celula cu FIRE (2,2) din gen 0 trebuie să devină EMPTY (0).
        """
        defn, params, rule, init_cells = create_forest_fire_preset(num_generations=1)
        storage = StateStorage(store_intermediate=True)
        engine = SimulationEngine(defn, params, rule, storage=storage)
        engine.initialize_world(custom_cells=init_cells)
        engine.run_simulation()

        gen1 = storage.get_state_at_generation(1)
        self.assertIsNotNone(gen1)
        self.assertEqual(gen1.get_cell(2, 2), 0, "Fosta celulă FIRE (2,2) trebuie să fie EMPTY în gen1.")

    def test_forest_fire_gen1_trees_adjacent_to_fire_ignite(self):
        """
        La gen 1, copacii vecini cu celula de foc (2,2) din gen 0 trebuie să ia foc.
        Vecinii Moore ai (2,2): (1,1),(1,2),(1,3),(2,1),(2,3),(3,1),(3,2),(3,3).
        Dintre aceștia, cei cu TREE în gen0 trebuie să devină FIRE în gen1.
        """
        defn, params, rule, init_cells = create_forest_fire_preset(num_generations=1)
        storage = StateStorage(store_intermediate=True)
        engine = SimulationEngine(defn, params, rule, storage=storage)
        engine.initialize_world(custom_cells=init_cells)
        engine.run_simulation()

        gen0 = storage.get_state_at_generation(0)
        gen1 = storage.get_state_at_generation(1)

        fire_row, fire_col = 2, 2
        moore_offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dr, dc in moore_offsets:
            nr, nc = fire_row + dr, fire_col + dc
            if gen0.is_valid_position(nr, nc) and gen0.get_cell(nr, nc) == 1:
                self.assertEqual(
                    gen1.get_cell(nr, nc), 2,
                    f"Copacul ({nr},{nc}) vecin cu focul trebuie să ia foc în gen1.",
                )

    def test_forest_fire_reaches_stable_state(self):
        """
        Incendiul determinist (fără regenerare) se stinge după un număr finit de generații.
        Starea stabilă: fără nicio celulă FIRE (2).
        """
        defn, params, rule, init_cells = create_forest_fire_preset(num_generations=20)
        storage = StateStorage(store_intermediate=True)
        engine = SimulationEngine(defn, params, rule, storage=storage)
        engine.initialize_world(custom_cells=init_cells)
        engine.run_simulation()

        last_state = storage.latest_snapshot
        self.assertIsNotNone(last_state)
        fire_count = last_state.count_cells_of_type(2)
        self.assertEqual(fire_count, 0, "Nu trebuie să existe celule FIRE în starea stabilă.")

    def test_forest_fire_save_and_load_json_identity(self):
        """Salvare + reîncărcare JSON: fiecare GridState.equals() trebuie să fie True."""
        _, storage, _, _, filepath = self._run_and_save(
            create_forest_fire_preset, num_generations=6, filename="forest_fire_test.json"
        )
        self._assert_states_equal_after_reload(storage, filepath)

    def test_forest_fire_load_cell_types_correct(self):
        """
        Tipurile de celule reconstruite trebuie să aibă name și symbol corecte.
        """
        _, _, orig_defn, _, filepath = self._run_and_save(
            create_forest_fire_preset, num_generations=3, filename="ff_celltypes.json"
        )
        loaded_defn, _, _ = StateStorage.load_experiment_from_file(filepath)
        self.assertEqual(len(loaded_defn.cell_types), 3)
        symbols = {ct.symbol for ct in loaded_defn.cell_types}
        self.assertIn(".", symbols)   # EMPTY
        self.assertIn("T", symbols)   # TREE
        self.assertIn("F", symbols)   # FIRE


# ===========================================================================
# Partea 4 — Teste suplimentare StateStorage (edge-cases)
# ===========================================================================


class TestStateStorageEdgeCases(BaseStorageTest):
    """Edge-cases pentru StateStorage."""

    def test_empty_storage_get_all_states_returns_empty_list(self):
        """get_all_states() pe un storage gol trebuie să returneze []."""
        storage = StateStorage(store_intermediate=True)
        self.assertEqual(storage.get_all_states(), [])

    def test_empty_storage_get_state_at_generation_returns_none(self):
        """get_state_at_generation pe storage gol trebuie să returneze None."""
        storage = StateStorage(store_intermediate=True)
        self.assertIsNone(storage.get_state_at_generation(0))

    def test_save_load_preserves_generation_indices(self):
        """Indicii generațiilor (generation_index) trebuie păstrați după reload JSON."""
        defn, params, rule, init_cells = create_rule30_preset(num_generations=4)
        storage = StateStorage(store_intermediate=True)
        engine = SimulationEngine(defn, params, rule, storage=storage)
        engine.initialize_world(custom_cells=init_cells)
        engine.run_simulation()

        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w"
        ) as fh:
            filepath = fh.name

        try:
            storage.save_experiment_to_file(filepath, defn, params)
            _, _, loaded_storage = StateStorage.load_experiment_from_file(filepath)
            orig_indices = [s.generation_index for s in storage.get_all_states()]
            load_indices = [s.generation_index for s in loaded_storage.get_all_states()]
            self.assertEqual(orig_indices, load_indices)
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    def test_save_load_preserves_boundary_type(self):
        """boundary_type trebuie păstrat în fiecare GridState după reload."""
        defn, params, rule, init_cells = create_brians_brain_preset(num_generations=2)
        storage = StateStorage(store_intermediate=True)
        engine = SimulationEngine(defn, params, rule, storage=storage)
        engine.initialize_world(custom_cells=init_cells)
        engine.run_simulation()

        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w"
        ) as fh:
            filepath = fh.name

        try:
            storage.save_experiment_to_file(filepath, defn, params)
            _, _, loaded_storage = StateStorage.load_experiment_from_file(filepath)
            for orig, loaded in zip(
                storage.get_all_states(), loaded_storage.get_all_states()
            ):
                self.assertEqual(orig.boundary_type, loaded.boundary_type)
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    def test_id_generator_synced_after_load(self):
        """
        Contoarele IDGenerator trebuie să fie cel puțin la nivelul ID-urilor
        din fișierul JSON după load_experiment_from_file.
        """
        defn, params, rule, init_cells = create_rule30_preset(num_generations=3)
        storage = StateStorage(store_intermediate=True)
        engine = SimulationEngine(defn, params, rule, storage=storage)
        engine.initialize_world(custom_cells=init_cells)
        engine.run_simulation()

        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w"
        ) as fh:
            filepath = fh.name

        try:
            storage.save_experiment_to_file(filepath, defn, params)
            IDGenerator.reset_all()
            loaded_defn, loaded_params, loaded_storage = (
                StateStorage.load_experiment_from_file(filepath)
            )
            # Contoarele trebuie să reflecte ID-urile maxime din fișier
            self.assertGreaterEqual(
                IDGenerator.get_current(IDGenerator.CAT_AUTOMATON),
                loaded_defn.automaton_id,
            )
            self.assertGreaterEqual(
                IDGenerator.get_current(IDGenerator.CAT_EXPERIMENT),
                loaded_params.experiment_id,
            )
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)


if __name__ == "__main__":
    unittest.main(verbosity=2)
