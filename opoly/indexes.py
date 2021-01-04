from typing import Optional
from enum import Enum

class IndexDescriptorType(Enum):
    ANY = "*"
    POSITIVE = "+"
    CONSTANT = ""


class IndexDescriptor():

    def __init__(self, vdtype: IndexDescriptorType, value: Optional[int] = None):  # pylint: disable=unsubscriptable-object
        self._vdtype = vdtype
        if vdtype == IndexDescriptorType.CONSTANT and value is None:
            raise ValueError(
                "Value cannot be None for constant type descriptor!")
        if vdtype != IndexDescriptorType.CONSTANT and value is not None:
            raise ValueError(
                "Value must be None for non constant type descriptor!")
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

    def __str__(self):
        return f"({','.join([str(descriptor) for descriptor in self.descriptors])})"

    def __repr__(self):
        return f"({','.join([repr(descriptor) for descriptor in self.descriptors])})"