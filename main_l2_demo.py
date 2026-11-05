from cellab.core.id_generator import IDGenerator
from cellab.presets.config_loader import load_preset_from_file
from cellab.engine.simulation_engine import SimulationEngine


def run_demo(config_path: str, label: str, show_stable: bool = False) -> None:
    print(f"=== {label} ===")
    defn, params, rule, init_cells = load_preset_from_file(config_path)
    engine = SimulationEngine(definition=defn, params=params, rule=rule)
    engine.initialize_world(custom_cells=init_cells)

    for s in engine.run_simulation():
        rendered = s.render_ascii(defn.cell_types)
        if params.height == 1:
            print(f"Gen {s.generation_index}: {rendered}")
        else:
            header = f"Gen {s.generation_index}"
            if show_stable:
                header += f" (Stabil: {engine.is_stable})"
            print(f"--- {header} ---")
            print(rendered)

    print(f"[OK] {label} finalizat.\n")


if __name__ == "__main__":
    run_demo("configs/rule30.json",       "DEMO 1: Rule 30 (1D)")
    IDGenerator.reset_all()
    run_demo("configs/brians_brain.json", "DEMO 2: Brian's Brain (2D)")
    IDGenerator.reset_all()
    run_demo("configs/forest_fire.json",  "DEMO 3: Forest Fire (2D)", show_stable=True)