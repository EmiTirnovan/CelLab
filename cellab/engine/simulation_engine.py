from cellab.core.models import AutomatonDefinition, ExperimentParams
from cellab.rules.transition_rule import TransitionRule
from cellab.world.grid import GridState
from cellab.world.initializer import WorldInitializer


class SimulationEngine:
    def __init__(self, definition: AutomatonDefinition, params: ExperimentParams,
                 rule: TransitionRule, storage=None):
        self.definition = definition
        self.params = params
        self.rule = rule
        self.storage = storage

        self._current_grid: GridState | None = None
        self._all_states: list[GridState] = []
        self.is_stable: bool = False

    def initialize_world(self, custom_cells: list[list[int]] | None = None) -> GridState:
        if custom_cells is not None:
            override_params = ExperimentParams(
                automaton_name=self.params.automaton_name,
                width=self.params.width,
                height=self.params.height,
                num_generations=self.params.num_generations,
                store_intermediate=self.params.store_intermediate,
                boundary_type=self.params.boundary_type,
                init_mode="CUSTOM",
                random_seed=self.params.random_seed,
                experiment_id=self.params.experiment_id,
            )
            grid = WorldInitializer.from_custom_matrix(override_params, custom_cells)
        elif self.params.init_mode == "CENTER_SEED":
            grid = WorldInitializer.from_center_seed(self.params, seed_state=1)
        elif self.params.init_mode == "RANDOM":
            grid = WorldInitializer.from_random(self.params, num_states=len(self.definition.cell_types))
        else:
            grid = GridState(
                width=self.params.width,
                height=self.params.height,
                generation_index=0,
                boundary_type=self.params.boundary_type,
            )

        self._current_grid = grid
        self._all_states = [grid]
        self.is_stable = False

        if self.storage is not None:
            self.storage.add_state(grid)

        return grid

    def step(self) -> GridState:
        if self._current_grid is None:
            raise RuntimeError("Lumea nu a fost inițializată. Apelați initialize_world() mai întâi.")

        current = self._current_grid
        next_grid = current.clone_for_next_generation()

        for r in range(current.height):
            for c in range(current.width):
                next_grid.set_cell(r, c, self.rule.apply(current, r, c, self.definition))

        self.is_stable = next_grid.equals(current)
        self._current_grid = next_grid
        self._all_states.append(next_grid)

        if self.storage is not None:
            self.storage.add_state(next_grid)

        return next_grid

    def run_simulation(self) -> list[GridState]:
        if self._current_grid is None:
            raise RuntimeError("Lumea nu a fost inițializată. Apelați initialize_world() mai întâi.")

        for _ in range(self.params.num_generations):
            self.step()
            if self.is_stable:
                break

        return self._all_states

    @property
    def current_grid(self) -> GridState | None:
        return self._current_grid

    @property
    def all_states(self) -> list[GridState]:
        return self._all_states
