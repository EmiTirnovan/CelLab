from cellab.rules.transition_rule import TransitionRule

_OFF = 0
_ON = 1
_DYING = 2


class BriansBrainRule(TransitionRule):
    def __init__(self, rule_id: int | None = None):
        super().__init__(name="Brian's Brain", rule_id=rule_id)

    def apply(self, grid, row: int, col: int, definition) -> int:
        current = grid.get_cell(row, col)

        if current == _ON:
            return _DYING

        if current == _DYING:
            return _OFF

        neighbors = grid.get_moore_neighbors(row, col)
        if grid.count_neighbors_in_state(neighbors, _ON) == 2:
            return _ON

        return _OFF
