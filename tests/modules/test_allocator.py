import numpy as np
import pytest

from opoly.modules.allocator import LamportCPAllocator

# @pytest.mark.skip(reason="too slow to test every time")
class TestLamportCPAllocator():

    def test_2d_identity(self):
        schedule = [1, 0]
        res, _ = LamportCPAllocator().allocate(np.array(schedule))
        assert res.tolist() == [[1, 0], [0, 1]]

    def test_2d_example1(self):
        schedule = [1, 1]
        res, _ = LamportCPAllocator().allocate(np.array(schedule))
        assert res.tolist() == [[1, 1], [0, 1]]

    def test_2d_example2(self):
        schedule = [2, 1]
        res, _ = LamportCPAllocator().allocate(np.array(schedule))
        assert res.tolist() == [[2, 1], [1, 0]]

    def test_2d_example3(self):
        schedule = [3, 2]
        res, _ = LamportCPAllocator().allocate(np.array(schedule))
        assert res.tolist() == [[3, 2], [1, 1]]

    def test_3d_example4(self):
        schedule = [1, 1, 1]
        res, _ = LamportCPAllocator().allocate(np.array(schedule))
        assert res.tolist() == [
            [1, 1, 1],
            [0, 1, 0],
            [0, 0, 1]
        ]

    def test_3d_example5(self):
        schedule = [2, 1, 1]
        res, _ = LamportCPAllocator().allocate(np.array(schedule))
        assert res.tolist() == [
            [2, 1, 1],
            [1, 0, 0],
            [0, 0, 1]
        ]

    def test_4d(self):
        schedule = [1, 1, 1, 1]
        res, _ = LamportCPAllocator().allocate(np.array(schedule))
        assert res.tolist() == [
            [1, 1, 1, 1],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]

    def test_timeout(self):
        schedule = [2, 2]
        res, _ = LamportCPAllocator().allocate(np.array(schedule))
        assert res is None

    def test_unsat(self):
        schedule = [-3, 2]
        res, _ = LamportCPAllocator().allocate(np.array(schedule))
        assert res is None

    def test_not_integer(self):
        schedule = [1.5, 0]
        res, _ = LamportCPAllocator().allocate(np.array(schedule))
        assert res is None
