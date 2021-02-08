import pytest

from opoly.expressions import (
    Expression,
    GroupingExpression,
    ConstantExpression,
    VariableExpression,
    FunctionExpression,
    UnaryExpression,
    extract_variable_expressions,
    divide_variable_expressions_by_name
)


class TestExpressions():

    def test_constant_expression(self):
        expr = ConstantExpression(1)
        assert str(expr) == "1"
        assert expr.is_constant()

    def test_simple_variable_expression(self):
        expr = VariableExpression("a")
        assert repr(expr) == "a"
        assert expr.is_variable()

    def test_indexed_variable_expression(self):
        expr = VariableExpression("a", [
            Expression(terms=[VariableExpression("i"),
                              ConstantExpression(1),
                              ],
                       operators=["+"]),
            Expression(terms=[VariableExpression("j"),
                              ConstantExpression(1),
                              ],
                       operators=["-"]),
        ])
        assert str(expr) == "a[i + 1][j - 1]"

    def test_grouping_expression(self):
        expr = GroupingExpression(terms=[
            VariableExpression("a"),
            VariableExpression("b"),
            VariableExpression("c"),
        ], operators=["+", "-"])
        assert str(expr) == "(a + b - c)"

    def test_function_expression(self):
        expr = FunctionExpression("max", (
            VariableExpression("i"),
            VariableExpression("j")
        ))
        assert expr.name == "max"
        assert str(expr) == "max(i, j)"
    
    def test_unary_expression(self):
        expr = UnaryExpression(VariableExpression("n"), "-")
        assert str(expr) == "-n"

    def test_empty_expression(self):
        with pytest.raises(ValueError):
            _ = Expression([], [])

    def test_wrong_operator_number(self):
        with pytest.raises(ValueError):
            _ = Expression([
                ConstantExpression(1),
                ConstantExpression(2),
            ], [])

    def test_is_sigle_expression(self):
        expr = ConstantExpression(1)
        assert expr.is_single()

    def test_is_not_sigle_expression(self):
        expr = Expression([
            VariableExpression("i"),
            VariableExpression("j"),
        ], ["+"])
        assert not expr.is_single()

    def test_is_simple_variable_expression(self):
        expr = VariableExpression("a")
        assert expr.is_simple()

    def test_is_not_simple_variable_expression(self):
        expr = VariableExpression("a", [VariableExpression("i")])
        assert not expr.is_simple()

    def test_simple_extract_variable_expressions(self):
        expr = GroupingExpression(terms=[
            VariableExpression("a"),
            VariableExpression("b"),
            VariableExpression("c"),
            ConstantExpression(1)
        ], operators=["+", "-", "+"])
        assert list(str(e) for e in extract_variable_expressions(expr)) == [
            "a", "b", "c"
        ]

    def test_extract_variable_expression_with_function(self):
        expr = FunctionExpression("max", (
            VariableExpression("i"),
            VariableExpression("j")
        ))
        assert list(str(e) for e in extract_variable_expressions(expr)) == [
            "i", "j"
        ]

    def test_complex_extract_variable_expressions(self):
        expr = Expression(
            terms=[
                GroupingExpression(terms=[
                    VariableExpression("a"),
                    VariableExpression("b"),
                    VariableExpression("c")
                ], operators=["+", "-"]),
                ConstantExpression(3)
            ],
            operators=["/"]
        )
        assert list(str(e) for e in extract_variable_expressions(expr)) == [
            "a", "b", "c"
        ]
    
    def test_divide_variable_expressions(self):
        expressions = [
            VariableExpression("a"),
            VariableExpression("b"),
            VariableExpression("a", [
                VariableExpression("i"),
                VariableExpression("j")
            ])
        ]
        expr_dict = divide_variable_expressions_by_name(expressions)
        assert list([str(e) for e in expr_dict["a"]]) == ["a", "a[i][j]"]
        assert list([str(e) for e in expr_dict["b"]]) == ["b"]
        assert "c" not in expr_dict
