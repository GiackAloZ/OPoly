import pytest

from opoly.variables import (
    SimpleVariableOccurrence,
    VariableOccurrenceType,
    VariableDescriptor,
    VariableDescriptorType,
    VariableSet
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
        assert str(occ) == "[GEN] VAR a[i+0][j-1]"

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


class TestVariableDescriptor():

    def test_constant(self):
        desc = VariableDescriptor(
            vdtype=VariableDescriptorType.CONSTANT,
            value=-1
        )
        assert desc.converted_value == -1
        assert str(desc) == "-1"
        assert repr(desc) == "-1"

    def test_any(self):
        desc = VariableDescriptor(
            vdtype=VariableDescriptorType.ANY
        )
        assert desc.converted_value == 1
        assert str(desc) == "*"
        assert repr(desc) == "1"

    def test_positive(self):
        desc = VariableDescriptor(
            vdtype=VariableDescriptorType.POSITIVE
        )
        assert desc.converted_value == 1
        assert str(desc) == "+"
        assert repr(desc) == "1"

    def test_wrong_constant(self):
        with pytest.raises(ValueError):
            _ = VariableDescriptor(
                vdtype=VariableDescriptorType.CONSTANT
            )

    def test_wrong_non_constant(self):
        with pytest.raises(ValueError):
            _ = VariableDescriptor(
                vdtype=VariableDescriptorType.POSITIVE,
                value=100
            )


class TestVariableSet():

    def test_simple(self):
        vset = VariableSet(
            descriptors=(
                VariableDescriptor(VariableDescriptorType.CONSTANT, 1),
                VariableDescriptor(VariableDescriptorType.CONSTANT, -1)
            )
        )
        assert vset.converted_values == (1, -1)
        assert str(vset) == "(1,-1)"
        assert repr(vset) == "(1,-1)"

    def test_complex(self):
        vset = VariableSet(
            descriptors=(
                VariableDescriptor(VariableDescriptorType.ANY),
                VariableDescriptor(VariableDescriptorType.CONSTANT, 1),
                VariableDescriptor(VariableDescriptorType.POSITIVE),
                VariableDescriptor(VariableDescriptorType.CONSTANT, -1)
            )
        )
        assert vset.converted_values == (1, 1, 1, -1)
        assert str(vset) == "(*,1,+,-1)"
        assert repr(vset) == "(1,1,1,-1)"

    def test_positive(self):
        vset = VariableSet(
            descriptors=(
                VariableDescriptor(VariableDescriptorType.ANY),
                VariableDescriptor(VariableDescriptorType.CONSTANT, -1),
                VariableDescriptor(VariableDescriptorType.CONSTANT, 1)
            )
        )
        assert vset.is_positive()

    def test_not_positive(self):
        vset = VariableSet(
            descriptors=(
                VariableDescriptor(VariableDescriptorType.CONSTANT, -1),
                VariableDescriptor(VariableDescriptorType.CONSTANT, 1)
            )
        )
        assert not vset.is_positive()

    def test_zeros(self):
        vset = VariableSet(
            descriptors=(
                VariableDescriptor(VariableDescriptorType.CONSTANT, 0),
                VariableDescriptor(VariableDescriptorType.CONSTANT, 0)
            )
        )
        assert vset.converted_values == (0, 0)
        assert str(vset) == "(0,0)"
        assert repr(vset) == "(0,0)"
        assert not vset.is_positive()

    def test_no_descriptors(self):
        with pytest.raises(ValueError):
            _ = VariableSet(descriptors=())
