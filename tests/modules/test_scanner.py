import pytest
import numpy as np
import sympy as sp

from opoly.expressions import Expression, VariableExpression, ConstantExpression, GroupingExpression
from opoly.statements import AssignmentStatement, ForLoopStatement
from opoly.modules.scanner import reindex, invert_integer_matrix
from opoly.modules.scanner import FourierMotzkinScanner


# @pytest.mark.skip(reason="too slow to test every time")
class TestReindexerFunctions():

    def test_example1(self):
        n, m = sp.symbols("n m", integers=True)
        i, j = sp.symbols("i j", integers=True)
        T = np.array([
            [1, 1],
            [0, 1]
        ], dtype=int)
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
        ], dtype=int)
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
        ], dtype=int)
        idxs = sp.Matrix([[i], [j]])
        ls = sp.Matrix([[1], [1]])
        us = sp.Matrix([[n], [m]])
        bounds = reindex(
            invert_integer_matrix(T),
            idxs,
            ls,
            us
        )
        assert bounds[j] == (sp.ceiling(sp.Max(1, sp.together((i - m)/2))),
                             sp.floor(sp.Min(n, sp.together((i - 1)/2))))
        assert bounds[i] == (3, 2*n + m)

    def test_example3(self):
        n, m = sp.symbols("n m", integers=True)
        i, j = sp.symbols("i j", integers=True)
        T = np.array([
            [3, 2],
            [1, 1]
        ], dtype=int)
        idxs = sp.Matrix([[i], [j]])
        ls = sp.Matrix([[1], [1]])
        us = sp.Matrix([[n], [m]])
        bounds = reindex(
            invert_integer_matrix(T),
            idxs,
            ls,
            us
        )
        assert bounds[j] == (sp.ceiling(sp.Max(sp.together((i - n)/2), sp.together((i + 1)/3))),
                             sp.floor(sp.Min(sp.together((i - 1)/2), sp.together((m + i)/3))))
        assert bounds[i] == (5, 3*n + 2*m)

    def test_example4(self):
        l, m, n = sp.symbols("l m n", integers=True)
        i, j, k = sp.symbols("i j k", integers=True)
        T = np.array([
            [1, 1, 1],
            [0, 1, 0],
            [0, 0, 1]
        ], dtype=int)
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
        ], dtype=int)
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
        assert bounds[j] == (sp.ceiling(sp.Max(1, sp.together((i - m - l)/2))),
                             sp.floor(sp.Min(n, sp.together((i - 2)/2))))
        assert bounds[i] == (4, 2*n + m + l)

    def test_example5a(self):
        l, m, n = sp.symbols("l m n", integers=True)
        i, j, k = sp.symbols("i j k", integers=True)
        T = np.array([
            [2, 1, 1],
            [1, 1, 0],
            [0, 0, 1]
        ], dtype=int)
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
        assert bounds[j] == (sp.ceiling(sp.Max(2, i - l - n, sp.together((i - l + 1)/2))),
                             sp.floor(sp.Min(i - 2, m + n, sp.together((i + m - 1)/2))))
        assert bounds[i] == (sp.Max(4, 5 - l, 5 - m),
                             sp.Min(l + m + 2*n, l + 2*m + 2*n - 1, 2*l + m + 2*n - 1))


# @pytest.mark.skip(reason="too slow to test every time")
class TestFourierMotzkinScanner():

    def test_1d_identity(self):
        loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )
        allocation = np.array([[1]])
        reindexed_loop = FourierMotzkinScanner().reindex(loop, allocation)
        assert reindexed_loop is not None

    def test_1d_identity2(self):
        loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=Expression(
                [VariableExpression("N"), ConstantExpression(1)], "-")
        )
        allocation = np.array([[1]])
        reindexed_loop = FourierMotzkinScanner().reindex(loop, allocation)
        assert reindexed_loop is not None

    def test_2d_identity(self):
        inner_loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("j")]),
                                      VariableExpression("b", [VariableExpression("j")]))],
            index=VariableExpression("j"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("M")
        )
        outer_loop = ForLoopStatement(
            body=[inner_loop],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )
        allocation = np.array([[1, 0], [0, 1]])
        reindexed_loop = FourierMotzkinScanner().reindex(outer_loop, allocation)
        assert reindexed_loop is not None

    def test_2d_example1(self):
        aij = VariableExpression(
            "a", [VariableExpression("i"), VariableExpression("j")])
        aiminus1j = VariableExpression("a", [Expression([
            VariableExpression("i"),
            ConstantExpression(1)],
            ["-"]),
            VariableExpression("j")
        ])
        aijminus1 = VariableExpression("a", [VariableExpression("i"),
                                             Expression([
                                                 VariableExpression("j"),
                                                 ConstantExpression(1)
                                             ], ["-"])
                                             ])
        inner_loop = ForLoopStatement(
            body=[AssignmentStatement(aij, Expression([
                GroupingExpression([aiminus1j, aij, aijminus1], ["+", "+"]),
                ConstantExpression(3.0)], ["/"]))],
            index=VariableExpression("j"),
            lowerbound=ConstantExpression(1),
            upperbound=Expression(
                [VariableExpression("M"), ConstantExpression(1)], "-")
        )
        outer_loop = ForLoopStatement(
            body=[inner_loop],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=Expression(
                [VariableExpression("N"), ConstantExpression(1)], "-")
        )
        allocation = np.array([[1, 1], [0, 1]])
        reindexed_loop = FourierMotzkinScanner().reindex(outer_loop, allocation)
        assert reindexed_loop is not None

    def test_3d_example5(self):
        ujk = VariableExpression("u",[
            VariableExpression("j"),
            VariableExpression("k")
        ])
        ujp1k = VariableExpression("u",[
            Expression([VariableExpression("j"), ConstantExpression(1)], ["+"]),
            VariableExpression("k")
        ])
        ujm1k = VariableExpression("u",[
            Expression([VariableExpression("j"), ConstantExpression(1)], ["-"]),
            VariableExpression("k")
        ])
        ujkp1 = VariableExpression("u",[
            VariableExpression("j"),
            Expression([VariableExpression("k"), ConstantExpression(1)], ["+"])
        ])
        ujkm1 = VariableExpression("u",[
            VariableExpression("j"),
            Expression([VariableExpression("k"), ConstantExpression(1)], ["-"])
        ])
        left = ujk
        right = Expression([
            GroupingExpression([ujp1k, ujm1k, ujkp1, ujkm1], ["+", "+", "+"]),
            ConstantExpression(0.25)
        ], ["/"])

        kloop = ForLoopStatement(
            body=[AssignmentStatement(left, right)],
            index=VariableExpression("k"),
            lowerbound=ConstantExpression(1),
            upperbound=Expression([VariableExpression("L"), ConstantExpression(2)], ["-"])
        )
        jloop = ForLoopStatement(
            body=[kloop],
            index=VariableExpression("j"),
            lowerbound=ConstantExpression(1),
            upperbound=Expression([VariableExpression("M"), ConstantExpression(2)], ["-"])
        )
        iloop = ForLoopStatement(
            body=[jloop],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )
        allocation = np.array([
            [2, 1, 1],
            [1, 0, 0],
            [0, 0, 1]
        ])
        reindexed_loop = FourierMotzkinScanner().reindex(iloop, allocation)
        assert reindexed_loop is not None
    
    def test_2d_indexes(self):
        aij = VariableExpression(
            "a", [VariableExpression("i"), VariableExpression("j")])
        aiminus1j = VariableExpression("a", [Expression([
            VariableExpression("i"),
            ConstantExpression(1)],
            ["-"]),
            VariableExpression("j")
        ])
        aijminus1 = VariableExpression("a", [VariableExpression("i"),
                                             Expression([
                                                 VariableExpression("j"),
                                                 ConstantExpression(1)
                                             ], ["-"])
                                             ])
        inner_loop = ForLoopStatement(
            body=[AssignmentStatement(aij, Expression([
                GroupingExpression([aiminus1j, aij, aijminus1], ["+", "+"]),
                ConstantExpression(3.0)], ["/"]))],
            index=VariableExpression("j"),
            lowerbound=ConstantExpression(1),
            upperbound=Expression(
                [VariableExpression("i"), ConstantExpression(2)], "+")
        )
        outer_loop = ForLoopStatement(
            body=[inner_loop],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=Expression(
                [VariableExpression("N"), ConstantExpression(1)], "-")
        )
        allocation = np.array([[1, 1], [0, 1]])
        reindexed_loop = FourierMotzkinScanner().reindex(outer_loop, allocation)
        assert reindexed_loop is not None
