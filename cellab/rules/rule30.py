from cellab.rules.transition_rule import TransitionRule


_RULE30_TABLE: dict[tuple[int, int, int], int] = {
    (1, 1, 1): 0,
    (1, 1, 0): 0,
    (1, 0, 1): 0,
    (1, 0, 0): 1,
    (0, 1, 1): 1,
    (0, 1, 0): 1,
    (0, 0, 1): 1,
    (0, 0, 0): 0,
}


class Rule30(TransitionRule):
    def __init__(self, rule_id: int | None = None):
        super().__init__(name="Rule 30", rule_id=rule_id)

    def apply(self, grid, row: int, col: int, definition) -> int:
        triplet = grid.get_elementary_1d_triplet(row, col)
        return _RULE30_TABLE.get(triplet, 0)
