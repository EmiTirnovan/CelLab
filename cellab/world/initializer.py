import random
from cellab.core.models import ExperimentParams
from cellab.world.grid import GridState

class WorldInitializer:
    @staticmethod
    def from_custom_matrix(params: ExperimentParams, matrix: list[list[int]]) -> GridState:
        if len(matrix) != params.height or any(len(row) != params.width for row in matrix):
            raise ValueError("Dimensiunile matricei custom nu corespund cu parametrii experimentului (width/height).")
        
        grid = GridState(
            width=params.width,
            height=params.height,
            generation_index=0,
            boundary_type=params.boundary_type
        )
        grid.cells = [row[:] for row in matrix]
        return grid

    @staticmethod
    def from_center_seed(params: ExperimentParams, seed_state: int = 1) -> GridState:
        grid = GridState(
            width=params.width,
            height=params.height,
            generation_index=0,
            boundary_type=params.boundary_type
        )
        mid_row = params.height // 2
        mid_col = params.width // 2
        grid.set_cell(mid_row, mid_col, seed_state)
        return grid

    @staticmethod
    def from_random(params: ExperimentParams, num_states: int) -> GridState:
        rng = random.Random(params.random_seed)
        grid = GridState(
            width=params.width,
            height=params.height,
            generation_index=0,
            boundary_type=params.boundary_type
        )
        for r in range(params.height):
            for c in range(params.width):
                grid.cells[r][c] = rng.randint(0, num_states - 1)
        return grid