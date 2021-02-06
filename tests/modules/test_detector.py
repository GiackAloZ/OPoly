from opoly.expressions import Expression, VariableExpression, ConstantExpression, GroupingExpression
from opoly.statements import ForLoopStatement, AssignmentStatement
from opoly.modules.detector import LamportLoopDependenciesDetector


class TestLamportDetector():

    def test_2d_loop(self):
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

        deps = LamportLoopDependenciesDetector().extract_dependencies(outer_loop)
        assert sorted(map(lambda x: x.converted_values, deps)) == [
            (0, 1), (1, -1), (1, 0), (1, 1)]

    def test_3d_loop(self):
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

        deps = LamportLoopDependenciesDetector().extract_dependencies(iloop)
        assert sorted(map(lambda x: x.converted_values, deps)) == [
            (0, 1, 0), (0, 1, 1), (1, -1, -1), (1, -1, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1)]
