from opoly.expressions import ConstantExpression, VariableExpression
from opoly.modules.parser import parse_constant_expression, parse_variable_expression, parse_expression


class TestParsingFunctions():

    def test_constant_parser(self):
        goods = {
            "0": (0, ""),
            "1": (1, ""),
            "0.5": (0.5, ""),
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
    
    def test_expression_parser(self):
        goods = {
            "a + i": ("a + i", ""),
            "a[i] + b[i]": ("a[i] + b[i]", ""),
            "a[i] + b[i] / 3": ("a[i] + b[i] / 3", ""),
            "a[i+1][j+1] + a[i-1][j-1] / 3": ("a[i + 1][j + 1] + a[i - 1][j - 1] / 3", "")
        }
        bads = {
            "": "Expected expression",
            "a +": "Expected expression",
            "a+": "Expected expression",
            "a+[": "Unsupported expression term",
            "[": "Unsupported expression term",
            "+": "Unsupported expression term",
            "a a": "Unsupported operator"
        }
        for code, res in goods.items():
            parsed, rem = parse_expression(code)
            assert parsed is not None
            assert str(parsed) == str(VariableExpression(res[0]))
            assert rem == res[1]
        for code, err in bads.items():
            parsed, error = parse_expression(code)
            assert parsed is None
            assert error == err
