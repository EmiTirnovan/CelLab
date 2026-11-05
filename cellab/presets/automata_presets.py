

from cellab.core.models import AutomatonDefinition, ExperimentParams
from cellab.rules.rule30 import Rule30
from cellab.rules.brians_brain import BriansBrainRule
from cellab.rules.forest_fire import ForestFireRule


# ==========================================================================
# Preset 1 — Rule 30 (Wolfram 1D)
# ==========================================================================

def create_rule30_preset(num_generations: int = 6) -> tuple:
    """
    Preset pentru automatul elementar Rule 30 (Wolfram 1D).

    Starea inițială: 1×13, cu un singur '1' în centru (col 6),
    exact ca în Documentul 1 al cursului.

    Stări:
        0 → DEAD  (simbol '.')
        1 → ALIVE (simbol '1')

    Parameters
    ----------
    num_generations : int
        Numărul de generații de simulat (implicit 6).

    Returns
    -------
    tuple
        (AutomatonDefinition, ExperimentParams, Rule30, init_cells)
    """
    defn = AutomatonDefinition(
        name="Rule 30 (Wolfram 1D)",
        dimension=1,
        neighborhood_type="ELEMENTARY_1D",
    )
    defn.add_cell_type(name="Dead",  symbol=".", color_hex="#1a1a2e")
    defn.add_cell_type(name="Alive", symbol="1", color_hex="#e94560")

    # Dimensiuni: 1 rând × 13 coloane — exact din Documentul 1
    width = 13
    params = ExperimentParams(
        automaton_name="Rule 30 (Wolfram 1D)",
        width=width,
        height=1,
        num_generations=num_generations,
        store_intermediate=True,
        boundary_type="FIXED",
        init_mode="CUSTOM",
        random_seed=42,
    )

    # Matricea inițială din Documentul 1: un singur '1' în mijloc (col 6)
    init_cells = [[0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]]

    return defn, params, Rule30(), init_cells


# ==========================================================================
# Preset 2 — Brian's Brain (2D, 3 stări)
# ==========================================================================

def create_brians_brain_preset(num_generations: int = 5) -> tuple:
    """
    Preset pentru Brian's Brain — automatul cu 3 stări (OFF/FIRING/DYING).

    Starea inițială: 3×5, exact ca în Documentul 1 al cursului:
        [[0,0,1,0,0],
         [0,1,0,1,0],
         [0,0,0,0,0]]

    Stări:
        0 → OFF    (simbol '.')
        1 → FIRING (simbol 'F')
        2 → DYING  (simbol 'D')

    Parameters
    ----------
    num_generations : int
        Numărul de generații de simulat (implicit 5).

    Returns
    -------
    tuple
        (AutomatonDefinition, ExperimentParams, BriansBrainRule, init_cells)
    """
    defn = AutomatonDefinition(
        name="Brian's Brain",
        dimension=2,
        neighborhood_type="MOORE",
    )
    defn.add_cell_type(name="Off",    symbol=".", color_hex="#0d0d1a")
    defn.add_cell_type(name="Firing", symbol="F", color_hex="#00d4ff")
    defn.add_cell_type(name="Dying",  symbol="D", color_hex="#0066ff")

    # Dimensiuni: 3 rânduri × 5 coloane — exact din Documentul 1
    params = ExperimentParams(
        automaton_name="Brian's Brain",
        width=5,
        height=3,
        num_generations=num_generations,
        store_intermediate=True,
        boundary_type="WRAP",
        init_mode="CUSTOM",
        random_seed=42,
    )

    # Matricea inițială din Documentul 1
    init_cells = [
        [0, 0, 1, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 0, 0, 0],
    ]

    return defn, params, BriansBrainRule(), init_cells


# ==========================================================================
# Preset 3 — Forest Fire (2D, 3 stări)
# ==========================================================================

def create_forest_fire_preset(num_generations: int = 6) -> tuple:
    """
    Preset pentru Forest Fire — automatul cu 3 stări (EMPTY/TREE/FIRE).

    Starea inițială: 4×5, exact ca în Documentul 1 al cursului:
        [[1,1,1,1,0],
         [1,1,0,1,1],
         [0,1,2,1,1],
         [1,1,1,1,1]]

    Stări:
        0 → EMPTY (simbol '.')
        1 → TREE  (simbol 'T')
        2 → FIRE  (simbol 'F')

    Parameters
    ----------
    num_generations : int
        Numărul de generații de simulat (implicit 6).

    Returns
    -------
    tuple
        (AutomatonDefinition, ExperimentParams, ForestFireRule, init_cells)
    """
    defn = AutomatonDefinition(
        name="Forest Fire",
        dimension=2,
        neighborhood_type="MOORE",
    )
    defn.add_cell_type(name="Empty", symbol=".", color_hex="#1a0a00")
    defn.add_cell_type(name="Tree",  symbol="T", color_hex="#228b22")
    defn.add_cell_type(name="Fire",  symbol="F", color_hex="#ff4500")

    # Dimensiuni: 4 rânduri × 5 coloane — exact din Documentul 1
    params = ExperimentParams(
        automaton_name="Forest Fire",
        width=5,
        height=4,
        num_generations=num_generations,
        store_intermediate=True,
        boundary_type="FIXED",
        init_mode="CUSTOM",
        random_seed=42,
    )

    # Matricea inițială din Documentul 1
    init_cells = [
        [1, 1, 1, 1, 0],
        [1, 1, 0, 1, 1],
        [0, 1, 2, 1, 1],
        [1, 1, 1, 1, 1],
    ]

    return defn, params, ForestFireRule(), init_cells
