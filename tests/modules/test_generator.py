from opoly.expressions import Expression, VariableExpression, ConstantExpression
from opoly.statements import ForLoopStatement, DeclarationStatement, AssignmentStatement
from opoly.modules.generator import PseudoCodeGenerator, CCodeGenerator


class TestPseudoCodeGenerator():

    def test_declaration(self):
        stmt = DeclarationStatement(
            var_type="",
            variable=VariableExpression("i"),
            initialization=ConstantExpression(1)
        )
        code = PseudoCodeGenerator().generate(stmt)
        assert code == "VAR i = 1;"

    def test_assignment(self):
        stmt = AssignmentStatement(
            left_term=VariableExpression("i"),
            right_term=VariableExpression("j")
        )
        code = PseudoCodeGenerator().generate(stmt)
        assert code == "STM i = j;"

    def test_simple_for_loop(self):
        stmt = ForLoopStatement(
            body=[
                DeclarationStatement(
                    var_type="",
                    variable=VariableExpression("x"),
                    initialization=ConstantExpression(1)
                ),
                AssignmentStatement(
                    left_term=VariableExpression(
                        "a", [VariableExpression("i")]),
                    right_term=Expression([
                        VariableExpression("x"),
                        ConstantExpression(1)
                    ], ["+"])
                )
            ],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )
        code = PseudoCodeGenerator().generate(stmt)
        assert code == "FOR i FROM 1 TO N STEP 1 {\n    VAR x = 1;\n    STM a[i] = x + 1;\n}"

    def test_nested_for_loop(self):
        inner_loop = ForLoopStatement(
            body=[
                DeclarationStatement(
                    var_type="",
                    variable=VariableExpression("x"),
                    initialization=ConstantExpression(1)
                ),
                AssignmentStatement(
                    left_term=VariableExpression(
                        "a", [VariableExpression("j")]),
                    right_term=Expression([
                        VariableExpression("x"),
                        ConstantExpression(1)
                    ], ["+"])
                )
            ],
            index=VariableExpression("j"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("M"),
            is_parallel=True
        )
        outer_loop = ForLoopStatement(
            body=[inner_loop],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )
        code = PseudoCodeGenerator().generate(outer_loop)
        assert code == "FOR i FROM 1 TO N STEP 1 {\n    FOR CONC j FROM 1 TO M STEP 1 {\n        VAR x = 1;\n        STM a[j] = x + 1;\n    }\n}"


class TestCCodeGenerator():

    def test_declaration(self):
        stmt = DeclarationStatement(
            var_type="int",
            variable=VariableExpression("i"),
            initialization=ConstantExpression(1)
        )
        code = CCodeGenerator().generate(stmt)
        assert code == "int i = 1;"

    def test_assignment(self):
        stmt = AssignmentStatement(
            left_term=VariableExpression("i"),
            right_term=VariableExpression("j")
        )
        code = CCodeGenerator().generate(stmt)
        assert code == "i = j;"

    def test_simple_for_loop(self):
        stmt = ForLoopStatement(
            body=[
                DeclarationStatement(
                    var_type="int",
                    variable=VariableExpression("x"),
                    initialization=ConstantExpression(1)
                ),
                AssignmentStatement(
                    left_term=VariableExpression(
                        "a", [VariableExpression("i")]),
                    right_term=Expression([
                        VariableExpression("x"),
                        ConstantExpression(1)
                    ], ["+"])
                )
            ],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )
        code = CCodeGenerator().generate(stmt)
        assert code == "for(int i = 1; i <= N; i++) {\n    int x = 1;\n    a[i] = x + 1;\n}"

    def test_nested_for_loop(self):
        inner_loop = ForLoopStatement(
            body=[
                DeclarationStatement(
                    var_type="int",
                    variable=VariableExpression("x"),
                    initialization=ConstantExpression(1)
                ),
                AssignmentStatement(
                    left_term=VariableExpression(
                        "a", [VariableExpression("j")]),
                    right_term=Expression([
                        VariableExpression("x"),
                        ConstantExpression(1)
                    ], ["+"])
                )
            ],
            index=VariableExpression("j"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("M"),
            is_parallel=True
        )
        outer_loop = ForLoopStatement(
            body=[inner_loop],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )
        code = CCodeGenerator().generate(outer_loop)
        assert code == "for(int i = 1; i <= N; i++) {\n    #pragma omp parallel for\n    for(int j = 1; j <= M; j++) {\n        int x = 1;\n        a[j] = x + 1;\n    }\n}"
