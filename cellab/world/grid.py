from cellab.core.id_generator import IDGenerator
from cellab.core.models import CellType

class Position:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    def is_within(self, height: int, width: int) -> bool:
        return 0 <= self.row < height and 0 <= self.col < width


class GridState:
    def __init__(self, width: int, height: int, generation_index: int = 0, 
                 boundary_type: str = "FIXED", default_border_state: int = 0, 
                 state_id: int | None = None):
        self.state_id = state_id if state_id is not None else IDGenerator.next_id(IDGenerator.CAT_GRID_STATE)
        self.generation_index = generation_index
        self.width = width
        self.height = height
        self.boundary_type = boundary_type
        self.default_border_state = default_border_state

        # Alocare matrice 2D ca listă de liste, populată cu starea de graniță implicită (0)
        self.cells: list[list[int]] = [
            [default_border_state for _ in range(width)] for _ in range(height)
        ]

    def is_valid_position(self, row: int, col: int) -> bool:
        return 0 <= row < self.height and 0 <= col < self.width

    def get_cell(self, row: int, col: int) -> int:
        if self.is_valid_position(row, col):
            return self.cells[row][col]
        
        if self.boundary_type == "WRAP":
            # Înfășurare toroidală (modulo)
            return self.cells[row % self.height][col % self.width]
        
        # Pentru graniță FIXED, returnăm valoarea implicită a marginii (de regulă 0)
        return self.default_border_state

    def set_cell(self, row: int, col: int, state_id: int) -> None:
        if not self.is_valid_position(row, col):
            raise IndexError(f"Poziție invalidă pe hartă: ({row}, {col}) pentru dimensiunile ({self.height}, {self.width})")
        self.cells[row][col] = state_id

    def clear(self, default_state: int = 0) -> None:
        for r in range(self.height):
            for c in range(self.width):
                self.cells[r][c] = default_state

    def clone_for_next_generation(self, new_state_id: int | None = None) -> 'GridState':
        next_gen_id = new_state_id if new_state_id is not None else IDGenerator.next_id(IDGenerator.CAT_GRID_STATE)
        cloned = GridState(
            width=self.width,
            height=self.height,
            generation_index=self.generation_index + 1,
            boundary_type=self.boundary_type,
            default_border_state=self.default_border_state,
            state_id=next_gen_id
        )
        # Copiere adâncă (deep copy) a matricii de celule
        cloned.cells = [row[:] for row in self.cells]
        return cloned

    def get_moore_neighbors(self, row: int, col: int) -> list[int]:
        neighbors = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                neighbors.append(self.get_cell(row + dr, col + dc))
        return neighbors

    def get_von_neumann_neighbors(self, row: int, col: int) -> list[int]:
        # Nord, Sud, Est, Vest
        directions = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        return [self.get_cell(row + dr, col + dc) for dr, dc in directions]

    def get_elementary_1d_triplet(self, row: int, col: int) -> tuple[int, int, int]:
        left = self.get_cell(row, col - 1)
        curr = self.get_cell(row, col)
        right = self.get_cell(row, col + 1)
        return (left, curr, right)

    def count_neighbors_in_state(self, neighbors: list[int], target_state: int) -> int:
        return sum(1 for n in neighbors if n == target_state)

    def count_cells_of_type(self, target_state: int) -> int:
        count = 0
        for r in range(self.height):
            for c in range(self.width):
                if self.cells[r][c] == target_state:
                    count += 1
        return count

    def equals(self, other: 'GridState') -> bool:
        if not other:
            return False
        if self.width != other.width or self.height != other.height:
            return False
        return self.cells == other.cells

    def render_ascii(self, cell_types: list[CellType]) -> str:
        rendered_rows = []
        for r in range(self.height):
            row_chars = []
            for c in range(self.width):
                state_id = self.cells[r][c]
                # Găsim simbolul corespunzător state_id-ului din cell_types
                symbol = "?"
                for ct in cell_types:
                    if ct.state_id == state_id:
                        symbol = ct.symbol
                        break
                row_chars.append(symbol)
            rendered_rows.append("".join(row_chars))
        return "\n".join(rendered_rows)