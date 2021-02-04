from opoly.statements import ForLoopStatement, AssignmentStatement
from opoly.expressions import VariableExpression, ConstantExpression, Expression, GroupingExpression

from opoly.modules.checker import is_perfectly_nested_loop, is_plain_loop, LamportForLoopChecker


class TestForLoopStatementChecks():

    def test_plain_loop(self):
        loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )
        assert is_plain_loop(loop)
        assert LamportForLoopChecker().check(loop)[0]

    def test_nested_loop(self):
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
        assert is_plain_loop(outer_loop)
        assert is_perfectly_nested_loop(outer_loop)
        assert LamportForLoopChecker().check(outer_loop)[0]

    def test_not_simple_index(self):
        loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("a", [VariableExpression("i")]),
            lowerbound=VariableExpression("i"),
            upperbound=VariableExpression("M")
        )
        assert not is_plain_loop(loop)
        assert not LamportForLoopChecker().check(loop)[0]

    def test_not_constant_lowerbound(self):
        loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("i"),
            lowerbound=VariableExpression("j"),
            upperbound=VariableExpression("N")
        )
        assert not is_plain_loop(loop)
        assert not LamportForLoopChecker().check(loop)[0]

    def test_not_simple_upperbound(self):
        loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("a", [VariableExpression("i")])
        )
        assert not is_plain_loop(loop)
        assert not LamportForLoopChecker().check(loop)[0]

    def test_not_constant_step(self):
        loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N"),
            step=VariableExpression("j")
        )
        assert not is_plain_loop(loop)
        assert not LamportForLoopChecker().check(loop)[0]

    def test_not_singular_increment_step(self):
        loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N"),
            step=ConstantExpression(2)
        )
        assert not is_plain_loop(loop)
        assert not LamportForLoopChecker().check(loop)[0]

    def test_perfectly_nested_loop(self):
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

        assert is_perfectly_nested_loop(outer_loop)
        assert LamportForLoopChecker().check(outer_loop)[0]

    def test_not_perfectly_nested_loop(self):
        inner_loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("j")]),
                                      VariableExpression("b", [VariableExpression("j")]))],
            index=VariableExpression("j"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("M")
        )

        outer_loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      VariableExpression("b", [VariableExpression("i")])),
                  inner_loop],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )

        assert not is_perfectly_nested_loop(outer_loop)
        assert not LamportForLoopChecker().check(outer_loop)[0]

    def test_plain_nested_loop(self):
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

        assert is_plain_loop(outer_loop)
        assert is_perfectly_nested_loop(outer_loop)
        assert LamportForLoopChecker().check(outer_loop)[0]

    def test_not_plain_nested_loop(self):
        inner_loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("j")]),
                                      VariableExpression("b", [VariableExpression("j")]))],
            index=VariableExpression("j"),
            lowerbound=VariableExpression("i"),
            upperbound=VariableExpression("M")
        )

        outer_loop = ForLoopStatement(
            body=[inner_loop],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )

        assert is_plain_loop(outer_loop)
        assert is_perfectly_nested_loop(outer_loop)
        assert LamportForLoopChecker().check(outer_loop)[0]


class TestLamportForLoopChecker():

    def test_simple_2d_loop(self):
        inner_loop = ForLoopStatement(
            body=[AssignmentStatement(
                left_term=VariableExpression("a", [VariableExpression("j")]),
                right_term=Expression([
                    GroupingExpression([
                        VariableExpression("a", [Expression([
                            VariableExpression("j"), ConstantExpression(1)], "-")]),
                        VariableExpression("a", [VariableExpression("j")]),
                        VariableExpression("a", [Expression([
                            VariableExpression("j"), ConstantExpression(1)], "+")])
                    ], ["+", "+"]),
                    ConstantExpression(3.0)
                ], "/")
            )],
            index=VariableExpression("j"),
            lowerbound=ConstantExpression(1),
            upperbound=Expression(
                [VariableExpression("M"), ConstantExpression(1)], ["-"])
        )

        outer_loop = ForLoopStatement(
            body=[inner_loop],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )

        assert is_plain_loop(outer_loop)
        assert is_perfectly_nested_loop(outer_loop)
        assert LamportForLoopChecker().check(outer_loop)[0]

    def test_simple_3d_loop(self):
        ajk = VariableExpression("a", [
            VariableExpression("j"),
            VariableExpression("k")
        ])
        ajminus1k = VariableExpression("a", [
            Expression([VariableExpression("j"),
                        ConstantExpression(1)], ["-"]),
            VariableExpression("k")
        ])
        ajminus1kminus1 = VariableExpression("a", [
            Expression([VariableExpression("j"),
                        ConstantExpression(1)], ["-"]),
            Expression([VariableExpression("k"),
                        ConstantExpression(1)], ["-"]),
        ])

        right = Expression([
            ajk, ajminus1k, ajminus1kminus1
        ], ["+", "-"])
        left = ajk

        kloop = ForLoopStatement(
            body=[AssignmentStatement(left, right)],
            index=VariableExpression("k"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("l")
        )

        jloop = ForLoopStatement(
            body=[kloop],
            index=VariableExpression("j"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("m")
        )

        iloop = ForLoopStatement(
            body=[jloop],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("n")
        )

        assert is_plain_loop(iloop)
        assert is_perfectly_nested_loop(iloop)
        assert LamportForLoopChecker().check(iloop)[0]
