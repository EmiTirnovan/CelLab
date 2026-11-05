from abc import ABC, abstractmethod
from cellab.core.id_generator import IDGenerator


class TransitionRule(ABC):
    def __init__(self, name: str, rule_id: int | None = None):
        self.rule_id = rule_id if rule_id is not None else IDGenerator.next_id(IDGenerator.CAT_RULE)
        self.name = name

    @abstractmethod
    def apply(self, grid, row: int, col: int, definition) -> int:
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(rule_id={self.rule_id}, name='{self.name}')"
