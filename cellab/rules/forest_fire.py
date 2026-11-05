from cellab.rules.transition_rule import TransitionRule

_EMPTY = 0
_TREE = 1
_FIRE = 2


class ForestFireRule(TransitionRule):
    def __init__(self, rule_id: int | None = None):
        super().__init__(name="Forest Fire", rule_id=rule_id)

    def apply(self, grid, row: int, col: int, definition) -> int:
        current = grid.get_cell(row, col)

        if current == _FIRE:
            return _EMPTY

        if current == _TREE:
            neighbors = grid.get_moore_neighbors(row, col)
            if grid.count_neighbors_in_state(neighbors, _FIRE) >= 1:
                return _FIRE
            return _TREE

        return _EMPTY
