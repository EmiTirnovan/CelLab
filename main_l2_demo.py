from cellab.core.id_generator import IDGenerator
from cellab.presets.automata_presets import create_rule30_preset, create_brians_brain_preset, create_forest_fire_preset
from cellab.engine.simulation_engine import SimulationEngine
from cellab.storage.state_storage import StateStorage
import os

def run_rule30_demo():
    print("=== DEMO 1: Rule 30 (1D) ===")
    defn, params, rule, init_cells = create_rule30_preset(num_generations=4)
    storage = StateStorage(store_intermediate=True)
    engine = SimulationEngine(definition=defn, params=params, rule=rule, storage=storage)
    
    engine.initialize_world(custom_cells=init_cells)
    states = engine.run_simulation()
    
    for s in states:
        print(f"Gen {s.generation_index}: {s.render_ascii(defn.cell_types)}")
    
    os.makedirs("saved_experiments", exist_ok=True)
    filepath = "saved_experiments/rule30_demo.json"
    storage.save_experiment_to_file(filepath, defn, params)
    print(experiment_loaded := StateStorage.load_experiment_from_file(filepath))
    print(f"[OK] Experiment salvat și reîncărcat cu succes în {filepath}\n")

def run_brians_brain_demo():
    print("=== DEMO 2: Brian's Brain (2D) ===")
    IDGenerator.reset_all()
    defn, params, rule, init_cells = create_brians_brain_preset(num_generations=3)
    storage = StateStorage(store_intermediate=True)
    engine = SimulationEngine(definition=defn, params=params, rule=rule, storage=storage)
    
    engine.initialize_world(custom_cells=init_cells)
    states = engine.run_simulation()
    
    for s in states:
        print(f"--- Gen {s.generation_index} ---")
        print(s.render_ascii(defn.cell_types))
    print("[OK] Brian's Brain demo finalizat.\n")

def run_forest_fire_demo():
    print("=== DEMO 3: Forest Fire (2D) ===")
    IDGenerator.reset_all()
    defn, params, rule, init_cells = create_forest_fire_preset(num_generations=4)
    storage = StateStorage(store_intermediate=True)
    engine = SimulationEngine(definition=defn, params=params, rule=rule, storage=storage)
    
    engine.initialize_world(custom_cells=init_cells)
    states = engine.run_simulation()
    
    for s in states:
        print(f"--- Gen {s.generation_index} (Stabil: {engine.is_stable}) ---")
        print(s.render_ascii(defn.cell_types))
    print("[OK] Forest Fire demo finalizat.\n")

if __name__ == "__main__":
    run_rule30_demo()
    run_brians_brain_demo()
    run_forest_fire_demo()