"""
main_l2_demo.py
----------------
Demo pentru Livrabilul 2 — CelLab.

Demonstrează:
  1. Rule 30  (1D, Wolfram)
  2. Brian's Brain (2D, 3 stări)
  3. Forest Fire  (2D, 3 stări)

Fiecare demo rulează simularea, afișează generațiile și demonstrează
salvarea/recuperarea stărilor în format JSON (cerință Livrabil 2).
"""

import os
from cellab.core.id_generator import IDGenerator
from cellab.engine.simulation_engine import SimulationEngine
from cellab.presets.automata_presets import (
    create_rule30_preset,
    create_brians_brain_preset,
    create_forest_fire_preset,
)
from cellab.storage.state_storage import StateStorage

SAVE_DIR = "saved_experiments"


# ---------------------------------------------------------------------------
# Demo 1 — Rule 30
# ---------------------------------------------------------------------------

def run_rule30_demo():
    print("=" * 50)
    print("DEMO 1: Rule 30 (1D, Wolfram)")
    print("=" * 50)

    defn, params, rule, init_cells = create_rule30_preset(num_generations=6)
    storage = StateStorage(store_intermediate=True)
    engine = SimulationEngine(definition=defn, params=params, rule=rule, storage=storage)

    engine.initialize_world(custom_cells=init_cells)
    engine.run_simulation()

    for s in storage.get_all_states():
        print(f"Gen {s.generation_index:2d}: {s.render_ascii(defn.cell_types)}")

    # Salvare JSON
    filepath = os.path.join(SAVE_DIR, "rule30_demo.json")
    storage.save_experiment_to_file(filepath, defn, params)
    print(f"\n[OK] Saved to: {filepath}")

    # Recuperare JSON
    _, _, loaded_storage = StateStorage.load_experiment_from_file(filepath)
    all_ok = all(
        orig.equals(loaded)
        for orig, loaded in zip(storage.get_all_states(), loaded_storage.get_all_states())
    )
    print(f"[OK] Verificare reload JSON: {'PASSED' if all_ok else 'FAILED'}\n")


# ---------------------------------------------------------------------------
# Demo 2 — Brian's Brain
# ---------------------------------------------------------------------------

def run_brians_brain_demo():
    print("=" * 50)
    print("DEMO 2: Brian's Brain (2D, 3 stari)")
    print("=" * 50)

    IDGenerator.reset_all()
    defn, params, rule, init_cells = create_brians_brain_preset(num_generations=5)
    storage = StateStorage(store_intermediate=True)
    engine = SimulationEngine(definition=defn, params=params, rule=rule, storage=storage)

    engine.initialize_world(custom_cells=init_cells)
    engine.run_simulation()

    for s in storage.get_all_states():
        print(f"--- Gen {s.generation_index} ---")
        print(s.render_ascii(defn.cell_types))

    # Salvare JSON
    filepath = os.path.join(SAVE_DIR, "brians_brain_demo.json")
    storage.save_experiment_to_file(filepath, defn, params)
    print(f"\n[OK] Saved to: {filepath}")

    # Recuperare JSON
    _, _, loaded_storage = StateStorage.load_experiment_from_file(filepath)
    all_ok = all(
        orig.equals(loaded)
        for orig, loaded in zip(storage.get_all_states(), loaded_storage.get_all_states())
    )
    print(f"[OK] Verificare reload JSON: {'PASSED' if all_ok else 'FAILED'}\n")


# ---------------------------------------------------------------------------
# Demo 3 — Forest Fire
# ---------------------------------------------------------------------------

def run_forest_fire_demo():
    print("=" * 50)
    print("DEMO 3: Forest Fire (2D, 3 stari)")
    print("=" * 50)

    IDGenerator.reset_all()
    defn, params, rule, init_cells = create_forest_fire_preset(num_generations=10)
    storage = StateStorage(store_intermediate=True)
    engine = SimulationEngine(definition=defn, params=params, rule=rule, storage=storage)

    engine.initialize_world(custom_cells=init_cells)
    engine.run_simulation()

    for s in storage.get_all_states():
        print(f"--- Gen {s.generation_index} (Stabil: {engine.is_stable}) ---")
        print(s.render_ascii(defn.cell_types))

    # Salvare JSON
    filepath = os.path.join(SAVE_DIR, "forest_fire_demo.json")
    storage.save_experiment_to_file(filepath, defn, params)
    print(f"\n[OK] Saved to: {filepath}")

    # Recuperare JSON
    _, _, loaded_storage = StateStorage.load_experiment_from_file(filepath)
    all_ok = all(
        orig.equals(loaded)
        for orig, loaded in zip(storage.get_all_states(), loaded_storage.get_all_states())
    )
    print(f"[OK] Verificare reload JSON: {'PASSED' if all_ok else 'FAILED'}\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    os.makedirs(SAVE_DIR, exist_ok=True)
    run_rule30_demo()
    run_brians_brain_demo()
    run_forest_fire_demo()