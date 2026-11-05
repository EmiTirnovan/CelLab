from cellab.core.models import AutomatonDefinition, ExperimentParams
from cellab.rules.rule30 import Rule30
from cellab.rules.brians_brain import BriansBrainRule
from cellab.rules.forest_fire import ForestFireRule


def create_rule30_preset(width: int = 23, num_generations: int = 5) -> tuple:
    defn = AutomatonDefinition(name="Rule 30 (Wolfram 1D)", dimension=1, neighborhood_type="ELEMENTARY_1D")
    defn.add_cell_type(name="Dead", symbol=".", color_hex="#1a1a2e")
    defn.add_cell_type(name="Alive", symbol="1", color_hex="#e94560")

    params = ExperimentParams(
        automaton_name="Rule 30 (Wolfram 1D)",
        width=width, height=1,
        num_generations=num_generations,
        store_intermediate=True,
        boundary_type="FIXED",
        init_mode="CUSTOM",
        random_seed=42,
    )

    mid = width // 2
    init_cells = [[0] * width]
    init_cells[0][mid] = 1

    return defn, params, Rule30(), init_cells


def create_brians_brain_preset(width: int = 15, height: int = 10, num_generations: int = 5) -> tuple:
    defn = AutomatonDefinition(name="Brian's Brain", dimension=2, neighborhood_type="MOORE")
    defn.add_cell_type(name="Off", symbol=".", color_hex="#0d0d1a")
    defn.add_cell_type(name="On", symbol="O", color_hex="#00d4ff")
    defn.add_cell_type(name="Dying", symbol="o", color_hex="#0066ff")

    params = ExperimentParams(
        automaton_name="Brian's Brain",
        width=width, height=height,
        num_generations=num_generations,
        store_intermediate=True,
        boundary_type="WRAP",
        init_mode="CUSTOM",
        random_seed=42,
    )

    init_cells = [[0] * width for _ in range(height)]
    cx, cy = height // 2, width // 2
    for r, c in [(cx - 1, cy), (cx, cy - 1), (cx, cy + 1), (cx + 1, cy), (cx - 1, cy - 1)]:
        if 0 <= r < height and 0 <= c < width:
            init_cells[r][c] = 1

    return defn, params, BriansBrainRule(), init_cells


def create_forest_fire_preset(width: int = 20, height: int = 10, num_generations: int = 5) -> tuple:
    defn = AutomatonDefinition(name="Forest Fire", dimension=2, neighborhood_type="MOORE")
    defn.add_cell_type(name="Empty", symbol=" ", color_hex="#1a0a00")
    defn.add_cell_type(name="Tree", symbol="T", color_hex="#228b22")
    defn.add_cell_type(name="Fire", symbol="*", color_hex="#ff4500")

    params = ExperimentParams(
        automaton_name="Forest Fire",
        width=width, height=height,
        num_generations=num_generations,
        store_intermediate=True,
        boundary_type="FIXED",
        init_mode="CUSTOM",
        random_seed=42,
    )

    init_cells = [[1] * width for _ in range(height)]
    cx, cy = height // 2, width // 2
    for dr in (0, 1):
        for dc in (0, 1):
            r, c = cx + dr, cy + dc
            if 0 <= r < height and 0 <= c < width:
                init_cells[r][c] = 2

    return defn, params, ForestFireRule(), init_cells
