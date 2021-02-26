from opoly.expressions import ConstantExpression, VariableExpression
from opoly.modules.parser import (
    parse_constant_expression,
    parse_variable_expression,
    parse_grouping_expression,
    parse_simple_function_expression,
    parse_function_expression,
    parse_operator,
    parse_expression,
    parse_assignment_statement,
    parse_unary_expression,
    PseudocodeForLoopParser
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

    def test_simple_function_parser(self):
        goods = {
            "max(a)": ("max(a)", ""),
            "max(a) + i": ("max(a)", " + i"),
            "max(a, b, c) + i": ("max(a, b, c)", " + i"),
        }
        bads = {
            "": "Expected function expression",
            "max": "Expected function expression",
            "max(a": "Expected function expression",
            "max(,a)": "Function expression not well formatted",
            "max(a b)": "Unsupported operator",
        }
        for code, res in goods.items():
            parsed, rem = parse_simple_function_expression(code)
            assert parsed is not None
            assert str(parsed) == res[0]
            assert rem == res[1]
        for code, err in bads.items():
            parsed, error = parse_simple_function_expression(code)
            assert parsed is None
            assert error == err
    
    def test_function_parser(self):
        goods = {
            "max(a)": ("max(a)", ""),
            "max(a) + i": ("max(a)", " + i"),
            "max(a, b, c) + i": ("max(a, b, c)", " + i"),
            "ceil(max(a, b), min(a, b, c))": ("ceil(max(a, b), min(a, b, c))", ""),
            "ceil(max(a, b/2), min(a, b, c))": ("ceil(max(a, b / 2), min(a, b, c))", "")
        }
        bads = {
            "": "Expected function expression",
            "max": "Expected (",
            "max(a": "Expected ,",
            "max(,a)": "Unsupported expression term",
            "max(a b)": "Unsupported operator",
        }
        for code, res in goods.items():
            parsed, rem = parse_function_expression(code)
            assert parsed is not None
            assert str(parsed) == res[0]
            assert rem == res[1]
        for code, err in bads.items():
            parsed, error = parse_function_expression(code)
            assert parsed is None
            assert error == err
    
    def test_unary_expression_parser(self):
        goods = {
            "-1": ("-1", ""),
            "-n": ("-n", ""),
            "-(n+1)": ("-(n + 1)", ""),
            "-(a[1]-1)": ("-(a[1] - 1)", ""),
            "- a": ("-a", "")
        }
        bads = {
            "--a": "Unsupported unary operator",
            "- -a": "Unsupported unary operator"
        }
        for code, res in goods.items():
            parsed, rem = parse_unary_expression(code)
            assert parsed is not None
            assert str(parsed) == res[0]
            assert rem == res[1]
        for code, err in bads.items():
            parsed, error = parse_unary_expression(code)
            assert parsed is None
            assert error == err

    def test_expression_parser(self):
        goods = {
            "1": ("1", ""),
            "a + i": ("a + i", ""),
            "a[i] + b[i]": ("a[i] + b[i]", ""),
            "a[i] + b[i] / 3": ("a[i] + b[i] / 3", ""),
            "a[i+1][j+1] + a[i-1][j-1] / 3": ("a[i + 1][j + 1] + a[i - 1][j - 1] / 3", ""),
            "(a[i+1][j+1] + a[i-1][j-1]) / 3.0": ("(a[i + 1][j + 1] + a[i - 1][j - 1]) / 3.0", ""),
            "(-n + i - 1) / 2.0": ("(-n + i - 1) / 2.0", ""),
            "floor(min(1, (1.0/3.0) * (2 * a + b), 2 * i), a + c)": ("floor(min(1, (1.0 / 3.0) * (2 * a + b), 2 * i), a + c)", "")
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


class TestPseudocodeForLoopParser():

    def test_simple_parse_loop_body(self):
        code = "STM a[i] = a[i+1];"
        stmts, err = PseudocodeForLoopParser().parse_loop_body(code)
        print(err)
        assert stmts is not None
        assert len(stmts) == 1
        assert str(stmts[0]) == "a[i] = a[i + 1]"

    def test_long_parse_loop_body(self):
        code = "STM a = 10;\nSTM b = a;\nSTM c[x] = a+b;"
        stmts, err = PseudocodeForLoopParser().parse_loop_body(code)
        print(err)
        assert stmts is not None
        assert len(stmts) == 3
        assert str(stmts[0]) == "a = 10"
        assert str(stmts[1]) == "b = a"
        assert str(stmts[2]) == "c[x] = a + b"

    def test_parse_1d_loop(self):
        code = "FOR i FROM 0 TO n { STM a[i]=a[i+1]; }"
        loop, err = PseudocodeForLoopParser().parse_for_loop(code)
        print(err)
        assert loop is not None
        assert len(loop.body) == 1
        assert str(loop.index) == "i"
        assert str(loop.lowerbound) == "0"
        assert str(loop.upperbound) == "n"
        assert str(loop.step) == "1"
        assert str(loop.body[0]) == "a[i] = a[i + 1]"

    def test_parse_plain_nested_2d_loop(self):
        code = "FOR i FROM 1 TO N - 1 STEP 1 { FOR j FROM 2 TO M-1 { STM a[j] = (a[j-1] + a[j] + a[j+1]) / 3.0; } }"
        loop, err = PseudocodeForLoopParser().parse_for_loop(code)
        print(err)
        assert loop is not None
        assert len(loop.body) == 1
        assert str(loop.index) == "i"
        assert str(loop.lowerbound) == "1"
        assert str(loop.upperbound) == "N - 1"
        assert str(loop.step) == "1"
        inner_loop = loop.body[0]
        assert inner_loop is not None
        assert len(inner_loop.body) == 1
        assert str(inner_loop.index) == "j"
        assert str(inner_loop.lowerbound) == "2"
        assert str(inner_loop.upperbound) == "M - 1"
        assert str(inner_loop.step) == "1"
        assert str(
            inner_loop.body[0]) == "a[j] = (a[j - 1] + a[j] + a[j + 1]) / 3.0"

    def test_wrong_inner_loop(self):
        code = "FOR i FROM 1 TO N - 1 STEP 1 { FOR j FROM 2 TO M { STM a[j] == (a[j-1] + a[j] + a[j+1]) / 3.0; } }"
        loop, err = PseudocodeForLoopParser().parse_for_loop(code)
        assert loop is None

    def test_unsupported_inner_statement_loop(self):
        code = "FOR i FROM 0 TO n { asd }"
        loop, err = PseudocodeForLoopParser().parse_for_loop(code)
        assert loop is None

    def test_expected_loop(self):
        code = ""
        loop, err = PseudocodeForLoopParser().parse_for_loop(code)
        assert loop is None
        code = "asdasd"
        loop, err = PseudocodeForLoopParser().parse_for_loop(code)
        assert loop is None

    def test_wrong_loop_index(self):
        code = "FOR 2 FROM 1 TO N {a = 1;}"
        loop, err = PseudocodeForLoopParser().parse_for_loop(code)
        assert loop is None

    def test_wrong_lowerbound(self):
        code = "FOR i FROM 2**2 TO N {STM a = 1;}"
        loop, err = PseudocodeForLoopParser().parse_for_loop(code)
        assert loop is None

    def test_wrong_upperbound(self):
        code = "FOR i FROM 1 TO N//2 {STM a = 1;}"
        loop, err = PseudocodeForLoopParser().parse_for_loop(code)
        assert loop is None

    def test_wrong_step(self):
        code = "FOR i FROM 1 TO N/2 STEP 2**2 {STM a = 1;}"
        loop, err = PseudocodeForLoopParser().parse_for_loop(code)
        assert loop is None

    def test_empty_body(self):
        code = "FOR i FROM 1 TO N/2 STEP j { }"
        loop, err = PseudocodeForLoopParser().parse_for_loop(code)
        assert loop is None
    
    def test_complex_loop(self):
        code = """
        FOR i FROM 0 TO N {
            STM a[i][0] = 0;
            FOR j FROM 1 TO M-1 {
                STM a[i][j] = a[i][j-1] + a[i][j+1];
                STM a[j][j] = 0;
            }
            STM a[N][M] = a[0][0];
        }
        """
        loop, err = PseudocodeForLoopParser().parse_for_loop(code)
        assert loop is not None
