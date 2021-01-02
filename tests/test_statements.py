import pytest

from opoly.expressions import (
    Expression,
    SingleExpression,
    GroupingExpression,
    ConstantExpression,
    VariableExpression
)

from opoly.statements import (
    StatementType,
    AssigmentStatement,
    ForLoopStatement,
    check_perfectly_nested_loop,
    check_plain_nested_loop
)


class TestAssignmentStatement():

    def test_simple_assignment(self):
        stmt = AssigmentStatement(
            left_term=VariableExpression("a"),
            right_term=ConstantExpression(1)
        )
        assert stmt.stm_type == StatementType.ASSIGNMENT
        assert str(stmt) == "a = 1"

    def test_complex_assigment(self):
        stmt = AssigmentStatement(
            left_term=VariableExpression("a",
                                         [VariableExpression("i"), VariableExpression("j")]),
            right_term=Expression([
                VariableExpression("a",
                                   [Expression([VariableExpression("i"), ConstantExpression(1)], ["+"]),
                                    Expression([VariableExpression("j"), ConstantExpression(1)], ["+"])]),
                VariableExpression("a",
                                   [Expression([VariableExpression("i"), ConstantExpression(1)], ["-"]),
                                    Expression([VariableExpression("j"), ConstantExpression(1)], ["-"])])
            ], ["+"])
        )
        assert str(stmt) == "a[i][j] = a[i + 1][j + 1] + a[i - 1][j - 1]"


class TestForLoopStatement():

    def test_plain_loop(self):
        loop = ForLoopStatement(
            body=[AssigmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                     VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )
        assert loop.is_plain()
        assert str(loop) == "FOR i = 1...N\na[i] = b[i]"

    def test_nested_loop(self):
        inner_loop = ForLoopStatement(
            body=[AssigmentStatement(VariableExpression("a", [VariableExpression("j")]),
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

        assert str(outer_loop) == "FOR i = 1...N\nFOR j = 1...M\na[j] = b[j]"

    def test_not_simple_index(self):
        loop = ForLoopStatement(
            body=[AssigmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                     VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("a", [VariableExpression("i")]),
            lowerbound=VariableExpression("i"),
            upperbound=VariableExpression("M")
        )
        assert not loop.is_plain()

    def test_not_constant_lowerbound(self):
        loop = ForLoopStatement(
            body=[AssigmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                     VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("i"),
            lowerbound=VariableExpression("j"),
            upperbound=VariableExpression("N")
        )
        assert not loop.is_plain()

    def test_not_simple_upperbound(self):
        loop = ForLoopStatement(
            body=[AssigmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                     VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("a", [VariableExpression("i")])
        )
        assert not loop.is_plain()

    def test_not_constant_step(self):
        loop = ForLoopStatement(
            body=[AssigmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                     VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N"),
            step=VariableExpression("j")
        )
        assert not loop.is_plain()

    def test_not_singular_increment_step(self):
        loop = ForLoopStatement(
            body=[AssigmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                     VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N"),
            step=ConstantExpression(2)
        )
        assert not loop.is_plain()

    def test_empty_loop(self):
        with pytest.raises(ValueError):
            _ = ForLoopStatement(body=[],
                                 index=VariableExpression("i"),
                                 lowerbound=ConstantExpression(1),
                                 upperbound=ConstantExpression(10)
                                 )

    def test_perfectly_nested_loop(self):
        inner_loop = ForLoopStatement(
            body=[AssigmentStatement(VariableExpression("a", [VariableExpression("j")]),
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

        assert check_perfectly_nested_loop(outer_loop)

    def test_not_perfectly_nested_loop(self):
        inner_loop = ForLoopStatement(
            body=[AssigmentStatement(VariableExpression("a", [VariableExpression("j")]),
                                     VariableExpression("b", [VariableExpression("j")]))],
            index=VariableExpression("j"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("M")
        )

        outer_loop = ForLoopStatement(
            body=[AssigmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                     VariableExpression("b", [VariableExpression("i")])),
                  inner_loop],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )

        assert not check_perfectly_nested_loop(outer_loop)

    def test_plain_nested_loop(self):
        inner_loop = ForLoopStatement(
            body=[AssigmentStatement(VariableExpression("a", [VariableExpression("j")]),
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

        assert check_plain_nested_loop(outer_loop)

    def test_not_plain_nested_loop(self):
        inner_loop = ForLoopStatement(
            body=[AssigmentStatement(VariableExpression("a", [VariableExpression("j")]),
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

        assert not check_plain_nested_loop(outer_loop)
