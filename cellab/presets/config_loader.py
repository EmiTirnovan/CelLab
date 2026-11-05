import json
from cellab.core.models import AutomatonDefinition, ExperimentParams
from cellab.rules.rule30 import Rule30
from cellab.rules.brians_brain import BriansBrainRule
from cellab.rules.forest_fire import ForestFireRule
from cellab.rules.transition_rule import TransitionRule

_RULE_MAP: dict[str, type[TransitionRule]] = {
    "Rule30": Rule30,
    "BriansBrainRule": BriansBrainRule,
    "ForestFireRule": ForestFireRule,
}


def load_preset_from_file(filepath: str) -> tuple:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    auto = data["automaton"]
    p = data["params"]

    defn = AutomatonDefinition(
        name=auto["name"],
        dimension=auto["dimension"],
        neighborhood_type=auto["neighborhood_type"],
    )
    for ct in auto["cell_types"]:
        defn.add_cell_type(
            name=ct["name"],
            symbol=ct["symbol"],
            color_hex=ct.get("color_hex", "#FFFFFF"),
        )

    params = ExperimentParams(
        automaton_name=auto["name"],
        width=p["width"],
        height=p["height"],
        num_generations=p["num_generations"],
        boundary_type=p.get("boundary_type", "FIXED"),
        init_mode=p.get("init_mode", "CUSTOM"),
        random_seed=p.get("random_seed", 42),
    )

    rule_cls = _RULE_MAP.get(auto["rule"])
    if rule_cls is None:
        raise ValueError(f"Regula '{auto['rule']}' nu este recunoscută. Valori valide: {list(_RULE_MAP)}")
    rule = rule_cls()

    init_cells = data.get("init_cells", None)

    return defn, params, rule, init_cells
