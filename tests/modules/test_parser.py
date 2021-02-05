from opoly.expressions import ConstantExpression, VariableExpression
from opoly.modules.parser import (
    parse_constant_expression,
    parse_variable_expression,
    parse_grouping_expression,
    parse_operator,
    parse_expression,
    parse_assignment_statement
)


class TestParsingFunctions():

    def test_constant_parser(self):
        goods = {
            "0": (0, ""),
            "1": (1, ""),
            "0.5": (0.5, ""),
            "3.0": (3.0, ""),
            "10": (10, ""),
            "1000000": (1000000, ""),
            "1 / 2": (1, " / 2"),
            "1a": (1, "a")
        }
        bads = [
            "-1",
            "a",
            "",
            "/"
        ]
        for code, res in goods.items():
            parsed, rem = parse_constant_expression(code)
            assert parsed is not None
            assert parsed.value == ConstantExpression(res[0]).value
            assert type(parsed.value) == type(ConstantExpression(res[0]).value)
            assert rem == res[1]
        for code in bads:
            parsed, rem = parse_constant_expression(code)
            assert parsed is None

    def test_simple_variable_parser(self):
        goods = {
            "a": ("a", ""),
            "alpha": ("alpha", ""),
            "a_b": ("a_b", ""),
            "a + 1": ("a", " + 1"),
            "a+1": ("a", "+1"),
            "a1": ("a", "1")
        }
        bads = {
            "": "Expected variable expression",
            "0": "Expected variable expression",
            "1": "Expected variable expression",
            "-1": "Expected variable expression",
            "1a": "Expected variable expression",
            "[asd]": "Expected variable expression"
        }
        for code, res in goods.items():
            parsed, rem = parse_variable_expression(code)
            assert parsed is not None
            assert str(parsed) == str(VariableExpression(res[0]))
            assert rem == res[1]
        for code, err in bads.items():
            parsed, error = parse_variable_expression(code)
            assert parsed is None
            assert error == err

    def test_indexed_variable_parser(self):
        goods = {
            "a[1]": ("a[1]", ""),
            "a[1][1]": ("a[1][1]", ""),
            "a[i]": ("a[i]", ""),
            "a[i+1]": ("a[i + 1]", ""),
            "a[i+1][j+1] + 1": ("a[i + 1][j + 1]", " + 1"),
            "a[a[i]]": ("a[a[i]]", ""),
            "a[i] + 1": ("a[i]", " + 1"),
            "a[i]+1": ("a[i]", "+1"),
            "a]": ("a", "]")
        }
        bads = {
            "a[": "Expected expression",
            "a[]": "Unsupported expression term",
            "a[[]": "Unsupported expression term",
            "a[a[i]": "Expected ]"
        }
        for code, res in goods.items():
            parsed, rem = parse_variable_expression(code)
            assert parsed is not None
            assert str(parsed) == str(VariableExpression(res[0]))
            assert rem == res[1]
        for code, err in bads.items():
            parsed, error = parse_variable_expression(code)
            assert parsed is None
            assert error == err

    def test_operator_parser(self):
        goods = {
            "+": ("+", ""),
            "-": ("-", ""),
            "*": ("*", ""),
            "/": ("/", ""),
            "/ i": ("/", " i"),
        }
        bads = {
            "": "Expected operator"
        }
        for code, res in goods.items():
            parsed, rem = parse_operator(code)
            assert parsed is not None
            assert str(parsed) == res[0]
            assert rem == res[1]
        for code, err in bads.items():
            parsed, error = parse_operator(code)
            assert parsed is None
            assert error == err

    def test_grouping_parser(self):
        goods = {
            "(a)": ("(a)", ""),
            "(a + b)": ("(a + b)", ""),
            "(a +b)": ("(a + b)", ""),
            "(a+b)": ("(a + b)", ""),
            "(a[i] + 1)": ("(a[i] + 1)", ""),
            "(a[i] + b[i][j+1]) / 3.0": ("(a[i] + b[i][j + 1])", " / 3.0")
        }
        bads = {
            "": "Expected (",
            "(": "Expected expression",
            ")": "Expected (",
            "(a": "Expected )",
            "(a a)": "Unsupported operator",
            "(a + )": "Unsupported expression term"
        }
        for code, res in goods.items():
            parsed, rem = parse_grouping_expression(code)
            assert parsed is not None
            assert str(parsed) == res[0]
            assert rem == res[1]
        for code, err in bads.items():
            parsed, error = parse_grouping_expression(code)
            assert parsed is None
            assert error == err

    def test_expression_parser(self):
        goods = {
            "a + i": ("a + i", ""),
            "a[i] + b[i]": ("a[i] + b[i]", ""),
            "a[i] + b[i] / 3": ("a[i] + b[i] / 3", ""),
            "a[i+1][j+1] + a[i-1][j-1] / 3": ("a[i + 1][j + 1] + a[i - 1][j - 1] / 3", ""),
            "(a[i+1][j+1] + a[i-1][j-1]) / 3.0": ("(a[i + 1][j + 1] + a[i - 1][j - 1]) / 3.0", ""),
        }
        bads = {
            "": "Expected expression",
            "a +": "Expected expression",
            "a+": "Expected expression",
            "a+[": "Unsupported expression term",
            "[": "Unsupported expression term",
            "+": "Unsupported expression term",
            "a a": "Unsupported operator",
            "]": "Unsupported expression term",
            "a]": "Unsupported operator",
            "[]": "Unsupported expression term",
            "(": "Expected expression"
        }
        for code, res in goods.items():
            parsed, rem = parse_expression(code)
            assert parsed is not None
            assert str(parsed) == res[0]
            assert rem == res[1]
        for code, err in bads.items():
            parsed, error = parse_expression(code)
            assert parsed is None
            assert error == err

        parsed, err = parse_expression("a,", term_char=")")
        assert parsed is None
        assert err == "Expected )"

    def test_assignment_statement_parser(self):
        goods = {
            "a = a + i": ("a = a + i", None),
            "a[i] = a + i": ("a[i] = a + i", None),
            "a[i+1] = a + i": ("a[i + 1] = a + i", None),
            "a = a[i] + b[i]": ("a = a[i] + b[i]", None),
            "a =a[i] + b[i] / 3": ("a = a[i] + b[i] / 3", None),
            "a=a[i+1][j+1] + a[i-1][j-1] / 3": ("a = a[i + 1][j + 1] + a[i - 1][j - 1] / 3", None),
            "a= (a[i+1][j+1] + a[i-1][j-1]) / 3.0": ("a = (a[i + 1][j + 1] + a[i - 1][j - 1]) / 3.0", None),
        }
        bads = {
            "": "Expected = operator",
            "a = b = c": "Expected only one = operator in assignment",
            "= a": "Expected variable expression",
            "a = ": "Expected expression",
            "a + a = a": "Expected only one variable expression for left term",
            "a = bc[": "Expected expression",
            "a = asd + asd +": "Expected expression",
            "a = ]": "Unsupported expression term",
        }
        for code, res in goods.items():
            parsed, rem = parse_assignment_statement(code)
            print(rem)
            assert parsed is not None
            assert str(parsed) == res[0]
            assert rem == res[1]
        for code, err in bads.items():
            parsed, error = parse_assignment_statement(code)
            assert parsed is None
            assert error == err
