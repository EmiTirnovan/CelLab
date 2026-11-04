from dataclasses import dataclass, field
from cellab.core.id_generator import IDGenerator

@dataclass
class CellType:
    state_id: int
    name: str
    symbol: str
    color_hex: str = "#FFFFFF"

    def validate(self) -> bool:
        if self.state_id < 0:
            raise ValueError("state_id nu poate fi negativ.")
        if not self.name or not self.name.strip():
            raise ValueError("Numele tipului de celula nu poate fi vid.")
        if len(self.symbol) != 1:
            raise ValueError("Simbolul unei celule trebuie sa aiba exact 1 caracter.")
        return True

    def to_tuple(self) -> tuple:
        return (self.state_id, self.name, self.symbol, self.color_hex)


class AutomatonDefinition:
    def __init__(self, name: str, dimension: int, neighborhood_type: str, automaton_id: int | None = None):
        self.automaton_id = automaton_id if automaton_id is not None else IDGenerator.next_id(IDGenerator.CAT_AUTOMATON)
        self.name = name
        self.dimension = dimension
        self.neighborhood_type = neighborhood_type
        self.cell_types: list[CellType] = []

    def add_cell_type(self, name: str, symbol: str, color_hex: str = "#FFFFFF") -> CellType:
        for ct in self.cell_types:
            if ct.name == name or ct.symbol == symbol:
                raise ValueError(f"Exista deja un tip de celula cu numele '{name}' sau simbolul '{symbol}'.")
        
        state_id = len(self.cell_types)
        new_cell_type = CellType(state_id=state_id, name=name, symbol=symbol, color_hex=color_hex)
        new_cell_type.validate()
        self.cell_types.append(new_cell_type)
        return new_cell_type

    def get_cell_type_by_id(self, state_id: int) -> CellType:
        if not self.is_valid_state(state_id):
            raise IndexError(f"State ID invalid: {state_id}")
        return self.cell_types[state_id]

    def is_valid_state(self, state_id: int) -> bool:
        return 0 <= state_id < len(self.cell_types)


class ExperimentParams:
    def __init__(self, automaton_name: str, width: int, height: int, num_generations: int,
                 store_intermediate: bool = True, boundary_type: str = "FIXED",
                 init_mode: str = "CUSTOM", random_seed: int = 42, experiment_id: int | None = None):
        self.experiment_id = experiment_id if experiment_id is not None else IDGenerator.next_id(IDGenerator.CAT_EXPERIMENT)
        self.automaton_name = automaton_name
        self.width = width
        self.height = height
        self.num_generations = num_generations
        self.store_intermediate = store_intermediate
        self.boundary_type = boundary_type
        self.init_mode = init_mode
        self.random_seed = random_seed
        self.validate()

    def validate(self) -> bool:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Dimensiunile hărții (width, height) trebuie să fie > 0.")
        if self.num_generations < 1:
            raise ValueError("Numărul de generații trebuie să fie cel puțin 1.")
        if self.boundary_type not in ("FIXED", "WRAP"):
            raise ValueError(f"Tip de graniță invalid: {self.boundary_type}. Folosește 'FIXED' sau 'WRAP'.")
        if self.init_mode not in ("CUSTOM", "RANDOM", "CENTER_SEED"):
            raise ValueError(f"Mod de inițializare invalid: {self.init_mode}.")
        return True