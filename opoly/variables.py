from enum import Enum, auto
from abc import ABC, abstractmethod


class VariableOccurrenceType(Enum):
    GENERATION = auto()
    USE = auto()


class VariableOccurrence(ABC):

    def __init__(self, name: str, vtype: VariableOccurrenceType):
        self._vtype = vtype
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def vtype(self) -> VariableOccurrenceType:
        return self._vtype

    @abstractmethod
    def stringify(self) -> str:
        vtype_str = {
            VariableOccurrenceType.GENERATION: "GEN",
            VariableOccurrenceType.USE: "USE",
        }
        return f"[{vtype_str[self.vtype]}] STM {self.name}"

    def __str__(self):
        return self.stringify()


class SimpleVariableOccurrence(VariableOccurrence):

    def __init__(self, name: str, vtype: VariableOccurrenceType, indexes: tuple[tuple[str, int]]):
        super().__init__(name, vtype)
        self._indexes = indexes

    @property
    def indexes(self) -> tuple[tuple[str, int]]:
        return self._indexes

    @property
    def indexes_names(self) -> tuple[str]:
        return tuple(idx for idx, offset in self._indexes)

    @property
    def offsets(self) -> tuple[int]:
        return tuple(offset for idx, offset in self._indexes)

    def stringify(self) -> str:
        return (f"{super().stringify()}"
                f"{''.join([f'[{idx}{offset:+}]' for idx, offset in self.indexes])}")
