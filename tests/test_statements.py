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
    AssignmentStatement,
    DeclarationStatement,
    ForLoopStatement,
    divide_assignments,
    prune_expressions
)


class TestAssignmentStatement():

    def test_simple_assignment(self):
        stmt = AssignmentStatement(
            left_term=VariableExpression("a"),
            right_term=ConstantExpression(1)
        )
        assert stmt.stype == StatementType.ASSIGNMENT
        assert str(stmt) == "a = 1"

    def test_complex_assigment(self):
        stmt = AssignmentStatement(
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

    def test_simple_divide_assignment(self):
        stmt = AssignmentStatement(
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
        gens, uses = divide_assignments([stmt])
        assert list(str(g) for g in gens) == ["a[i][j]"]
        assert list(str(u) for u in uses) == [
            "a[i + 1][j + 1]", "a[i - 1][j - 1]"]
        gens, uses = prune_expressions(gens, uses)
        assert list(str(g) for g in gens) == ["a[i][j]"]
        assert list(str(u) for u in uses) == [
            "a[i + 1][j + 1]", "a[i - 1][j - 1]"]

    def test_complex_divide_and_prune_assignments(self):
        stmt1 = AssignmentStatement(
            left_term=VariableExpression("a",
                                         [VariableExpression("i"), VariableExpression("j")]),
            right_term=Expression([
                GroupingExpression([
                    VariableExpression("b",
                                       [Expression([VariableExpression("i"), ConstantExpression(1)], ["+"]),
                                        Expression([VariableExpression("j"), ConstantExpression(1)], ["+"])]),
                    VariableExpression("b",
                                       [Expression([VariableExpression("i"), ConstantExpression(1)], ["-"]),
                                        Expression([VariableExpression("j"), ConstantExpression(1)], ["-"])])
                ], ["+"]),
                ConstantExpression(2.0)
            ], ["/"])
        )
        assert str(
            stmt1) == "a[i][j] = (b[i + 1][j + 1] + b[i - 1][j - 1]) / 2.0"

        stmt2 = AssignmentStatement(
            left_term=VariableExpression("b",
                                         [VariableExpression("i"), VariableExpression("j")]),
            right_term=Expression([
                GroupingExpression([
                    VariableExpression("c",
                                       [Expression([VariableExpression("i"), ConstantExpression(1)], ["+"]),
                                        Expression([VariableExpression("j"), ConstantExpression(1)], ["+"])]),
                    VariableExpression("c",
                                       [Expression([VariableExpression("i"), ConstantExpression(1)], ["-"]),
                                        Expression([VariableExpression("j"), ConstantExpression(1)], ["-"])])
                ], ["+"]),
                ConstantExpression(2.0)
            ], ["/"])
        )
        assert str(
            stmt2) == "b[i][j] = (c[i + 1][j + 1] + c[i - 1][j - 1]) / 2.0"

        gens, uses = divide_assignments([stmt1, stmt2])
        assert list(str(g) for g in gens) == [
            "a[i][j]", "b[i][j]"
        ]
        assert list(str(u) for u in uses) == [
            "b[i + 1][j + 1]", "b[i - 1][j - 1]",
            "c[i + 1][j + 1]", "c[i - 1][j - 1]"
        ]
        pruned_gens, pruned_uses = prune_expressions(gens, uses)
        assert list(str(g) for g in pruned_gens) == ["b[i][j]"]
        assert list(str(u) for u in pruned_uses) == [
            "b[i + 1][j + 1]", "b[i - 1][j - 1]"
        ]

        stmt3 = AssignmentStatement(
            left_term=VariableExpression("a",
                                         [Expression([VariableExpression("i"), ConstantExpression(1)], ["+"]),
                                          VariableExpression("j")]),
            right_term=Expression([
                GroupingExpression([
                    VariableExpression("c",
                                       [Expression([VariableExpression("i"), ConstantExpression(1)], ["+"]),
                                        Expression([VariableExpression("j"), ConstantExpression(1)], ["+"])]),
                    VariableExpression("c",
                                       [Expression([VariableExpression("i"), ConstantExpression(1)], ["-"]),
                                        Expression([VariableExpression("j"), ConstantExpression(1)], ["-"])])
                ], ["+"]),
                ConstantExpression(2.0)
            ], ["/"])
        )
        assert str(
            stmt3) == "a[i + 1][j] = (c[i + 1][j + 1] + c[i - 1][j - 1]) / 2.0"

        gens, uses = divide_assignments([stmt1, stmt2, stmt3])
        assert list(str(g) for g in gens) == [
            "a[i][j]", "b[i][j]", "a[i + 1][j]"
        ]
        assert list(str(u) for u in uses) == [
            "b[i + 1][j + 1]", "b[i - 1][j - 1]",
            "c[i + 1][j + 1]", "c[i - 1][j - 1]",
            "c[i + 1][j + 1]", "c[i - 1][j - 1]"
        ]
        pruned_gens, pruned_uses = prune_expressions(gens, uses)
        assert list(str(g) for g in pruned_gens) == [
            "a[i][j]", "b[i][j]", "a[i + 1][j]"
        ]
        assert list(str(u) for u in pruned_uses) == [
            "b[i + 1][j + 1]", "b[i - 1][j - 1]"
        ]


class TestDeclarationStatement():
    
    def test_simple_declaration(self):
        stmt = DeclarationStatement(
            var_type="int",
            variable=VariableExpression("i")
        )
        assert stmt.stype == StatementType.DECLARATION
        assert str(stmt) == "int i"
    
    def test_complex_declaration(self):
        stmt = DeclarationStatement(
            var_type="int",
            variable=VariableExpression("i"),
            initialization=Expression([
                VariableExpression("j"),
                ConstantExpression(2)
            ], ["-"])
        )
        assert stmt.stype == StatementType.DECLARATION
        assert str(stmt) == "int i = j - 2"

class TestForLoopStatement():

    def test_plain_loop(self):
        loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )
        assert str(loop) == "FOR i = 1...N\na[i] = b[i]"

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
        assert str(outer_loop) == "FOR i = 1...N\nFOR j = 1...M\na[j] = b[j]"

    def test_empty_loop(self):
        with pytest.raises(ValueError):
            _ = ForLoopStatement(body=[],
                                 index=VariableExpression("i"),
                                 lowerbound=ConstantExpression(1),
                                 upperbound=ConstantExpression(10)
                                 )
