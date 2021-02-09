import pytest

from opoly.variables import (
    SimpleVariableOccurrence,
    VariableOccurrenceType
)


class TestSimpleVariableOccurrence():

    def test_simple(self):
        occ = SimpleVariableOccurrence(
            name="a",
            vtype=VariableOccurrenceType.GENERATION,
            indexes=(
                ("i", 0),
                ("j", -1)
            )
        )
        assert str(occ) == "[GEN] STM a[i+0][j-1]"

    def test_indexes_names(self):
        occ = SimpleVariableOccurrence(
            name="a",
            vtype=VariableOccurrenceType.GENERATION,
            indexes=(
                ("i", 1),
                ("j", -1)
            )
        )
        assert occ.indexes_names == ("i", "j")

    def test_offsets(self):
        occ = SimpleVariableOccurrence(
            name="a",
            vtype=VariableOccurrenceType.GENERATION,
            indexes=(
                ("i", 1),
                ("j", -1)
            )
        )
        assert occ.offsets == (1, -1)
