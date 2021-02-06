import pytest
import numpy as np
import sympy as sp

from opoly.modules.reindexer import reindex, invert_integer_matrix

@pytest.mark.skip(reason="too slow to test every time")
class TestReindexer():

    def test_example1(self):
        n, m = sp.symbols("n m", integers=True)
        i, j = sp.symbols("i j", integers=True)
        T = np.array([
            [1, 1],
            [0, 1]
        ], dtype=np.int)
        idxs = sp.Matrix([[i], [j]])
        ls = sp.Matrix([[1], [1]])
        us = sp.Matrix([[n], [m]])
        bounds = reindex(
            invert_integer_matrix(T),
            idxs,
            ls,
            us
        )
        assert bounds[j] == (sp.Max(1, i - n), sp.Min(m, i - 1))
        assert bounds[i] == (2, n + m)

    def test_example1a(self):
        n, m = sp.symbols("n m", integers=True)
        i, j = sp.symbols("i j", integers=True)
        T = np.array([
            [1, 1],
            [1, 0]
        ], dtype=np.int)
        idxs = sp.Matrix([[i], [j]])
        ls = sp.Matrix([[1], [1]])
        us = sp.Matrix([[n], [m]])
        bounds = reindex(
            invert_integer_matrix(T),
            idxs,
            ls,
            us
        )
        assert bounds[j] == (sp.Max(1, i - m), sp.Min(n, i - 1))
        assert bounds[i] == (2, n + m)

    def test_example2(self):
        n, m = sp.symbols("n m", integers=True)
        i, j = sp.symbols("i j", integers=True)
        T = np.array([
            [2, 1],
            [1, 0]
        ], dtype=np.int)
        idxs = sp.Matrix([[i], [j]])
        ls = sp.Matrix([[1], [1]])
        us = sp.Matrix([[n], [m]])
        bounds = reindex(
            invert_integer_matrix(T),
            idxs,
            ls,
            us
        )
        assert bounds[j] == (sp.Max(1, sp.ceiling(sp.together((i - m)/2))),
                             sp.Min(n, sp.floor(sp.together((i - 1)/2))))
        assert bounds[i] == (3, 2*n + m)
    
    def test_example3(self):
        n, m = sp.symbols("n m", integers=True)
        i, j = sp.symbols("i j", integers=True)
        T = np.array([
            [3, 2],
            [1, 1]
        ], dtype=np.int)
        idxs = sp.Matrix([[i], [j]])
        ls = sp.Matrix([[1], [1]])
        us = sp.Matrix([[n], [m]])
        bounds = reindex(
            invert_integer_matrix(T),
            idxs,
            ls,
            us
        )
        assert bounds[j] == (sp.Max(sp.ceiling(sp.together((i - n)/2)), sp.ceiling(sp.together((i + 1)/3))),
                             sp.Min(sp.floor(sp.together((i - 1)/2)), sp.floor(sp.together((m + i)/3))))
        assert bounds[i] == (5, 3*n + 2*m)
    
    def test_example4(self):
        l, m, n = sp.symbols("l m n", integers=True)
        i, j, k = sp.symbols("i j k", integers=True)
        T = np.array([
            [1, 1, 1],
            [0, 1, 0],
            [0, 0, 1]
        ], dtype=np.int)
        idxs = sp.Matrix([[i], [j], [k]])
        ls = sp.Matrix([[1], [1], [1]])
        us = sp.Matrix([[n], [m], [l]])
        bounds = reindex(
            invert_integer_matrix(T),
            idxs,
            ls,
            us
        )
        assert bounds[k] == (sp.Max(1, i - j - n),
                             sp.Min(l, i - j - 1))
        assert bounds[j] == (sp.Max(1, i - n - l),
                             sp.Min(m, i - 2))
        assert bounds[i] == (3, n + m + l)
    
    def test_example5(self):
        l, m, n = sp.symbols("l m n", integers=True)
        i, j, k = sp.symbols("i j k", integers=True)
        T = np.array([
            [2, 1, 1],
            [1, 0, 0],
            [0, 0, 1]
        ], dtype=np.int)
        idxs = sp.Matrix([[i], [j], [k]])
        ls = sp.Matrix([[1], [1], [1]])
        us = sp.Matrix([[n], [m], [l]])
        bounds = reindex(
            invert_integer_matrix(T),
            idxs,
            ls,
            us
        )
        assert bounds[k] == (sp.Max(1, i - 2*j - m),
                             sp.Min(l, i - 2*j - 1))
        assert bounds[j] == (sp.Max(1, sp.ceiling(sp.together((i - m - l)/2))),
                             sp.Min(n, sp.floor(sp.together((i - 2)/2))))
        assert bounds[i] == (4, 2*n + m + l)

    def test_example6(self):
        l, m, n = sp.symbols("l m n", integers=True)
        i, j, k = sp.symbols("i j k", integers=True)
        T = np.array([
            [2, 1, 1],
            [1, 1, 0],
            [0, 0, 1]
        ], dtype=np.int)
        idxs = sp.Matrix([[i], [j], [k]])
        ls = sp.Matrix([[1], [1], [1]])
        us = sp.Matrix([[n], [m], [l]])
        bounds = reindex(
            invert_integer_matrix(T),
            idxs,
            ls,
            us
        )
        assert bounds[k] == (sp.Max(1, i - 2*j + 1, i - j - n),
                             sp.Min(l, i - 2*j + m, i - j - 1))
        assert bounds[j] == (sp.Max(2, i - l - n, sp.ceiling(sp.together((i - l + 1)/2))),
                             sp.Min(i - 2, m + n, sp.floor(sp.together((i + m - 1)/2))))
        assert bounds[i] == (sp.Max(4, 5 - l, 5 - m),
                             sp.Min(l + m + 2*n, l + 2*m + 2*n - 1, 2*l + m + 2*n - 1))
