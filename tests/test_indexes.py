import pytest

from opoly.indexes import (
    IndexDescriptorType,
    IndexDescriptor,
    IndexSet
)


class TestIndexDescriptor():

    def test_constant(self):
        desc = IndexDescriptor(
            vdtype=IndexDescriptorType.CONSTANT,
            value=-1
        )
        assert desc.converted_value == -1
        assert str(desc) == "-1"
        assert repr(desc) == "-1"

    def test_any(self):
        desc = IndexDescriptor(
            vdtype=IndexDescriptorType.ANY
        )
        assert desc.converted_value == 1
        assert str(desc) == "*"
        assert repr(desc) == "1"

    def test_positive(self):
        desc = IndexDescriptor(
            vdtype=IndexDescriptorType.POSITIVE
        )
        assert desc.converted_value == 1
        assert str(desc) == "+"
        assert repr(desc) == "1"

    def test_wrong_constant(self):
        with pytest.raises(ValueError):
            _ = IndexDescriptor(
                vdtype=IndexDescriptorType.CONSTANT
            )

    def test_wrong_non_constant(self):
        with pytest.raises(ValueError):
            _ = IndexDescriptor(
                vdtype=IndexDescriptorType.POSITIVE,
                value=100
            )


class TestIndexSet():

    def test_simple(self):
        vset = IndexSet(
            descriptors=(
                IndexDescriptor(IndexDescriptorType.CONSTANT, 1),
                IndexDescriptor(IndexDescriptorType.CONSTANT, -1)
            )
        )
        assert vset.converted_values == (1, -1)
        assert str(vset) == "(1,-1)"
        assert repr(vset) == "(1,-1)"
        assert list([str(s) for s in vset.extract_positives()]) == [
            "(1,-1)"
        ]

    def test_any(self):
        vset = IndexSet(
            descriptors=(
                IndexDescriptor(IndexDescriptorType.ANY),
                IndexDescriptor(IndexDescriptorType.CONSTANT, 1)
            )
        )
        assert vset.converted_values == (1, 1)
        assert str(vset) == "(*,1)"
        assert repr(vset) == "(1,1)"
        assert list([str(s) for s in vset.extract_positives()]) == [
            "(0,1)",
            "(+,1)"
        ]

    def test_complex(self):
        vset = IndexSet(
            descriptors=(
                IndexDescriptor(IndexDescriptorType.ANY),
                IndexDescriptor(IndexDescriptorType.CONSTANT, 1),
                IndexDescriptor(IndexDescriptorType.POSITIVE),
                IndexDescriptor(IndexDescriptorType.CONSTANT, -1)
            )
        )
        assert vset.converted_values == (1, 1, 1, -1)
        assert str(vset) == "(*,1,+,-1)"
        assert repr(vset) == "(1,1,1,-1)"
        assert list([str(s) for s in vset.extract_positives()]) == [
            "(0,1,+,-1)",
            "(+,1,+,-1)"
        ]

    def test_successive_any_alone(self):
        vset = IndexSet(
            descriptors=(
                IndexDescriptor(IndexDescriptorType.ANY),
                IndexDescriptor(IndexDescriptorType.ANY)
            )
        )
        assert vset.converted_values == (1, 1)
        assert str(vset) == "(*,*)"
        assert repr(vset) == "(1,1)"
        assert list([str(s) for s in vset.extract_positives()]) == [
            "(0,+)",
            "(+,0)",
            "(+,+)"
        ]

    def test_successive_any_with_positive_constant(self):
        vset = IndexSet(
            descriptors=(
                IndexDescriptor(IndexDescriptorType.ANY),
                IndexDescriptor(IndexDescriptorType.ANY),
                IndexDescriptor(IndexDescriptorType.CONSTANT, 1),
            )
        )
        assert vset.converted_values == (1, 1, 1)
        assert str(vset) == "(*,*,1)"
        assert repr(vset) == "(1,1,1)"
        assert list([str(s) for s in vset.extract_positives()]) == [
            "(0,0,1)",
            "(0,+,1)",
            "(+,0,1)",
            "(+,+,1)"
        ]

    def test_successive_any_with_negative_constant(self):
        vset = IndexSet(
            descriptors=(
                IndexDescriptor(IndexDescriptorType.ANY),
                IndexDescriptor(IndexDescriptorType.ANY),
                IndexDescriptor(IndexDescriptorType.CONSTANT, -1),
            )
        )
        assert vset.converted_values == (1, 1, -1)
        assert str(vset) == "(*,*,-1)"
        assert repr(vset) == "(1,1,-1)"
        assert list([str(s) for s in vset.extract_positives()]) == [
            "(0,+,-1)",
            "(+,0,-1)",
            "(+,+,-1)"
        ]

    def test_multiple_any(self):
        vset = IndexSet(
            descriptors=(
                IndexDescriptor(IndexDescriptorType.ANY),
                IndexDescriptor(IndexDescriptorType.CONSTANT, -1),
                IndexDescriptor(IndexDescriptorType.ANY),
            )
        )
        assert vset.converted_values == (1, -1, 1)
        assert str(vset) == "(*,-1,*)"
        assert repr(vset) == "(1,-1,1)"
        assert list([str(s) for s in vset.extract_positives()]) == [
            "(+,-1,0)",
            "(+,-1,+)"
        ]

    def test_positive(self):
        vset = IndexSet(
            descriptors=(
                IndexDescriptor(IndexDescriptorType.ANY),
                IndexDescriptor(IndexDescriptorType.CONSTANT, -1),
                IndexDescriptor(IndexDescriptorType.CONSTANT, 1)
            )
        )
        assert vset.is_lexico_positive()

    def test_not_positive(self):
        vset = IndexSet(
            descriptors=(
                IndexDescriptor(IndexDescriptorType.CONSTANT, -1),
                IndexDescriptor(IndexDescriptorType.CONSTANT, 1)
            )
        )
        assert not vset.is_lexico_positive()

    def test_zeros(self):
        vset = IndexSet(
            descriptors=(
                IndexDescriptor(IndexDescriptorType.CONSTANT, 0),
                IndexDescriptor(IndexDescriptorType.CONSTANT, 0)
            )
        )
        assert vset.converted_values == (0, 0)
        assert str(vset) == "(0,0)"
        assert repr(vset) == "(0,0)"
        assert not vset.is_lexico_positive()

    def test_no_descriptors(self):
        with pytest.raises(ValueError):
            _ = IndexSet(descriptors=())
