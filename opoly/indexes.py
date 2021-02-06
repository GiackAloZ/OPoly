from __future__ import annotations

from typing import Optional
from enum import Enum


class IndexDescriptorType(Enum):
    ANY = "*"
    POSITIVE = "+"
    CONSTANT = ""


class IndexDescriptor():

    def __init__(self, vdtype: IndexDescriptorType, value: Optional[int] = None):  # pylint: disable=unsubscriptable-object
        if vdtype == IndexDescriptorType.CONSTANT and value is None:
            raise ValueError(
                "Value cannot be None for constant type descriptor!")
        if vdtype != IndexDescriptorType.CONSTANT and value is not None:
            raise ValueError(
                "Value must be None for non constant type descriptor!")
        self._vdtype = vdtype
        self._value = value

    @property
    def vdtype(self) -> IndexDescriptorType:
        return self._vdtype

    @property
    def converted_value(self) -> int:
        return self._value if self.vdtype == IndexDescriptorType.CONSTANT else 1

    def __str__(self):
        return f"{self.vdtype.value}{self._value if self._value is not None else ''}"

    def __repr__(self):
        return f"{self.converted_value}"


class IndexSet():

    def __init__(self, descriptors: tuple[IndexDescriptor]):
        if len(descriptors) == 0:
            raise ValueError("There must be at least one variable descriptor!")
        self._descriptors = descriptors

    @property
    def descriptors(self) -> tuple[IndexDescriptor]:
        return self._descriptors

    @property
    def converted_values(self) -> tuple[int]:
        return tuple(descriptor.converted_value for descriptor in self.descriptors)

    def is_lexico_positive(self) -> bool:
        for v in self.converted_values:
            if v > 0:
                return True
            if v < 0:
                return False
        return False

    def extract_positives(self) -> list[IndexSet]:
        expanded_sets = [self]
        # Expand * into 0 and +
        for i, desc in enumerate(self.descriptors):
            if desc.vdtype == IndexDescriptorType.ANY:
                new_sets = []
                for exp_set in expanded_sets:
                    exp_descs = list(exp_set.descriptors)
                    zero_descs = exp_descs[:i] + [IndexDescriptor(
                        IndexDescriptorType.CONSTANT, 0)] + exp_descs[i+1:]
                    plus_descs = exp_descs[:i] + [IndexDescriptor(
                        IndexDescriptorType.POSITIVE)] + exp_descs[i+1:]
                    zero_set = IndexSet(zero_descs)
                    plus_set = IndexSet(plus_descs)
                    if zero_set.is_lexico_positive():
                        new_sets.append(zero_set)
                    new_sets.append(plus_set)
                expanded_sets = new_sets
        # Filter out non-positive sets
        return list(filter(lambda s: s.is_lexico_positive(), expanded_sets))
    
    def to_converted(self) -> IndexSet:
        return IndexSet(list([
            IndexDescriptor(IndexDescriptorType.CONSTANT, value=v) for v in self.converted_values
        ]))

    def __str__(self):
        return f"({','.join([str(descriptor) for descriptor in self.descriptors])})"

    def __repr__(self):
        return f"({','.join([repr(descriptor) for descriptor in self.descriptors])})"

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(tuple([str(d) for d in self.descriptors]))