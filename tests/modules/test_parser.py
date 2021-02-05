from opoly.expressions import ConstantExpression
from opoly.modules.parser import parse_constant_expression


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
            print(parsed, rem)
            assert parsed is not None
            assert parsed.value == ConstantExpression(res[0]).value
            assert type(parsed.value) == type(ConstantExpression(res[0]).value)
            assert rem == res[1]
        for code in bads:
            parsed, rem = parse_constant_expression(code)
            print(parsed, rem)
            assert parsed is None