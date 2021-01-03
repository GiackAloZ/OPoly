from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Optional


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
        return f"[{vtype_str[self.vtype]}] VAR {self.name}"

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


class VariableDescriptorType(Enum):
    ANY = "*"
    POSITIVE = "+"
    CONSTANT = ""


class VariableDescriptor():

    def __init__(self, vdtype: VariableDescriptorType, value: Optional[int] = None):  # pylint: disable=unsubscriptable-object
        self._vdtype = vdtype
        if vdtype == VariableDescriptorType.CONSTANT and value is None:
            raise ValueError(
                "Value cannot be None for constant type descriptor!")
        if vdtype != VariableDescriptorType.CONSTANT and value is not None:
            raise ValueError(
                "Value must be None for non constant type descriptor!")
        self._value = value

    @property
    def vdtype(self) -> VariableDescriptorType:
        return self._vdtype

    @property
    def converted_value(self) -> int:
        return self._value if self.vdtype == VariableDescriptorType.CONSTANT else 1

    def __str__(self):
        return f"{self.vdtype.value}{self._value if self._value is not None else ''}"

    def __repr__(self):
        return f"{self.converted_value}"


class VariableSet():

    def __init__(self, descriptors: tuple[VariableDescriptor]):
        if len(descriptors) == 0:
            raise ValueError("There must be at least one variable descriptor!")
        self._descriptors = descriptors

    @property
    def descriptors(self) -> tuple[VariableDescriptor]:
        return self._descriptors

    @property
    def converted_values(self) -> tuple[int]:
        return tuple(descriptor.converted_value for descriptor in self.descriptors)

    def is_positive(self) -> bool:
        for v in self.converted_values:
            if v > 0:
                return True
            if v < 0:
                return False
        return False

    def __str__(self):
        return f"({','.join([str(descriptor) for descriptor in self.descriptors])})"

    def __repr__(self):
        return f"({','.join([repr(descriptor) for descriptor in self.descriptors])})"
