from opoly.statements import ForLoopStatement, AssigmentStatement
from opoly.expressions import ConstantExpression, VariableExpression
from opoly.checks import (
    check_perfectly_nested_loop,
    check_plain_nested_loop,
)


def test_perfectly_nested_loop():
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


def test_not_perfectly_nested_loop():
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


def test_plain_nested_loop():
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

def test_not_plain_nested_loop():
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