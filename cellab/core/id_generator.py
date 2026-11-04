class IDGenerator:
    CAT_AUTOMATON: int = 0
    CAT_EXPERIMENT: int = 1
    CAT_GRID_STATE: int = 2
    CAT_RULE: int = 3

    _counters: list[int] = [0, 0, 0, 0]

    @classmethod
    def next_id(cls, category: int) -> int:
        if category < 0 or category >= len(cls._counters):
            raise ValueError(f"Categorie de ID invalida: {category}")
        cls._counters[category] += 1
        return cls._counters[category]

    @classmethod
    def get_current(cls, category: int) -> int:
        if category < 0 or category >= len(cls._counters):
            raise ValueError(f"Categorie de ID invalida: {category}")
        return cls._counters[category]

    @classmethod
    def reset_all(cls) -> None:
        for i in range(len(cls._counters)):
            cls._counters[i] = 0

    @classmethod
    def sync_counter(cls, category: int, min_value: int) -> None:
        if category < 0 or category >= len(cls._counters):
            raise ValueError(f"Categorie de ID invalida: {category}")
        if min_value > cls._counters[category]:
            cls._counters[category] = min_value