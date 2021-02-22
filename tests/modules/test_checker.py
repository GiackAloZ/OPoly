from opoly.statements import ForLoopStatement, AssignmentStatement, DeclarationStatement
from opoly.expressions import VariableExpression, ConstantExpression, Expression, GroupingExpression

from opoly.modules.checker import is_perfectly_nested_loop, is_plain_loop, is_recursively_plain_loop, LamportForLoopChecker


class TestForLoopStatementChecks():

    def test_plain_loop(self):
        loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )
        assert is_plain_loop(loop)
        assert LamportForLoopChecker().check(loop)[0]

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
        assert is_plain_loop(outer_loop)
        assert is_perfectly_nested_loop(outer_loop)
        assert LamportForLoopChecker().check(outer_loop)[0]

    def test_not_simple_index(self):
        loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("a", [VariableExpression("i")]),
            lowerbound=VariableExpression("i"),
            upperbound=VariableExpression("M")
        )
        assert not is_plain_loop(loop)
        assert not LamportForLoopChecker().check(loop)[0]

    def test_not_constant_lowerbound(self):
        loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("i"),
            lowerbound=VariableExpression("j"),
            upperbound=VariableExpression("N")
        )
        assert not is_plain_loop(loop)
        assert not LamportForLoopChecker().check(loop)[0]

    def test_not_simple_upperbound(self):
        loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("a", [VariableExpression("i")])
        )
        assert not is_plain_loop(loop)
        assert not LamportForLoopChecker().check(loop)[0]

    def test_not_constant_step(self):
        loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N"),
            step=VariableExpression("j")
        )
        assert not is_plain_loop(loop)
        assert not LamportForLoopChecker().check(loop)[0]

    def test_not_singular_increment_step(self):
        loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N"),
            step=ConstantExpression(2)
        )
        assert not is_plain_loop(loop)
        assert not LamportForLoopChecker().check(loop)[0]

    def test_perfectly_nested_loop(self):
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

        assert is_perfectly_nested_loop(outer_loop)
        assert LamportForLoopChecker().check(outer_loop)[0]

    def test_not_perfectly_nested_loop(self):
        inner_loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("j")]),
                                      VariableExpression("b", [VariableExpression("j")]))],
            index=VariableExpression("j"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("M")
        )

        outer_loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      VariableExpression("b", [VariableExpression("i")])),
                  inner_loop],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )

        assert not is_perfectly_nested_loop(outer_loop)
        assert not LamportForLoopChecker().check(outer_loop)[0]

    def test_plain_nested_loop(self):
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

        assert is_plain_loop(outer_loop)
        assert is_perfectly_nested_loop(outer_loop)
        assert LamportForLoopChecker().check(outer_loop)[0]

    def test_not_plain_nested_loop(self):
        inner_loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("j")]),
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

        assert not is_recursively_plain_loop(outer_loop)
        assert is_perfectly_nested_loop(outer_loop)


class TestLamportForLoopChecker():

    def test_simple_2d_loop(self):
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

        assert is_plain_loop(outer_loop)
        assert is_perfectly_nested_loop(outer_loop)
        assert LamportForLoopChecker().check(outer_loop)[0]

    def test_simple_3d_loop(self):
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

        assert is_plain_loop(iloop)
        assert is_perfectly_nested_loop(iloop)
        assert LamportForLoopChecker().check(iloop)[0]

    def test_not_simple_indexes(self):
        loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("i", [ConstantExpression(0)]),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )
        res, error = LamportForLoopChecker().check(loop)
        assert not res
        assert error == "Loop indexes are not simple!"

    def test_not_all_distinct_indexes(self):
        inner_loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("M")
        )
        outer_loop = ForLoopStatement(
            body=[inner_loop],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )
        res, error = LamportForLoopChecker().check(outer_loop)
        assert not res
        assert error == "Not all index names in loop are distinct!"

    def test_not_all_assigments(self):
        loop = ForLoopStatement(
            body=[DeclarationStatement(var_type="int", variable=VariableExpression("x")),
                  AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )
        res, error = LamportForLoopChecker().check(loop)
        assert not res
        assert error == "Not all statements in loop body are assignments!"

    def test_not_all_left_variables(self):
        loop = ForLoopStatement(
            body=[AssignmentStatement(ConstantExpression(1),
                                      VariableExpression("b", [VariableExpression("i")]))],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )
        res, error = LamportForLoopChecker().check(loop)
        assert not res
        assert error == "Not all left sides of statements in loop body are variable expressions!"

    def test_not_all_non_simple_generations(self):
        loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a"),
                                      VariableExpression("a", [VariableExpression("i")]))],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )
        res, error = LamportForLoopChecker().check(loop)
        assert not res
        assert error == "All variable generations must be non-simple!"

    def test_not_all_same_name_simple_or_indexed(self):
        loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      Expression([
                                          VariableExpression(
                                              "a", [VariableExpression("i")]),
                                          VariableExpression("a")
                                      ], ["+"]
            ))],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )
        res, error = LamportForLoopChecker().check(loop)
        assert not res
        assert error == "Same name variables must be all simple or all non-simple!"

    def test_variable_index_not_present(self):
        wrong = VariableExpression("a", [VariableExpression("j")])
        loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      wrong)],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )
        res, error = LamportForLoopChecker().check(loop)
        assert not res
        assert error == f"Variable expression ({str(wrong)}) has an index not present in loop indexes!"

    def test_not_unique_variable_indexes(self):
        wrong = VariableExpression(
            "a", [VariableExpression("j"), VariableExpression("j")])
        inner_loop = ForLoopStatement(
            body=[AssignmentStatement(
                left_term=wrong,
                right_term=Expression([
                    GroupingExpression([
                        VariableExpression("a", [Expression([
                            VariableExpression("j"), ConstantExpression(1)], "-"), VariableExpression("j")]),
                        VariableExpression(
                            "a", [VariableExpression("j"), VariableExpression("j")]),
                        VariableExpression("a", [Expression([
                            VariableExpression("j"), ConstantExpression(1)], "+"), VariableExpression("j")])
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
        res, error = LamportForLoopChecker().check(outer_loop)
        assert not res
        assert error == f"Variable expression ({str(wrong)}) indexes are not unique!"

    def test_wrong_missing_index(self):
        wrong = VariableExpression("a", [VariableExpression("i")])
        inner_loop = ForLoopStatement(
            body=[AssignmentStatement(
                left_term=VariableExpression("a", [VariableExpression("i")]),
                right_term=Expression([
                    GroupingExpression([
                        VariableExpression("a", [Expression([
                            VariableExpression("i"), ConstantExpression(1)], "-")]),
                        VariableExpression("a", [VariableExpression("i")]),
                        VariableExpression("a", [Expression([
                            VariableExpression("i"), ConstantExpression(1)], "+")])
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
        res, error = LamportForLoopChecker().check(outer_loop)
        assert not res
        assert error == f"Variable expression ({str(wrong)}) has a missing index which is not ({outer_loop.index})!"

    def test_not_integer_constant(self):
        wrong = VariableExpression(
            "a", [Expression([VariableExpression("i"), ConstantExpression(1.5)], ["+"])])
        loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      wrong)],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )
        res, error = LamportForLoopChecker().check(loop)
        assert not res
        assert error == f"Variable expression ({str(wrong)}) has a non-integer constant in one of the indexes!"

    def test_not_simple_variable_indexes(self):
        wrong = VariableExpression(
            "a", [VariableExpression("i", [ConstantExpression(1)])])
        loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      wrong)],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )
        res, error = LamportForLoopChecker().check(loop)
        assert not res
        assert error == f"Variable expression ({str(wrong)}) has incorrect indexes!"

    def test_multiple_variable_indexes(self):
        wrong = VariableExpression(
            "a", [Expression([VariableExpression("i"), VariableExpression("j")], ["+"])])
        loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      wrong)],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )
        res, error = LamportForLoopChecker().check(loop)
        assert not res
        assert error == f"Variable expression ({str(wrong)}) has incorrect indexes!"

    def test_inverted_order_index_expression(self):
        wrong = VariableExpression("a", [Expression([
            ConstantExpression(1), VariableExpression("j")], "-")])
        inner_loop = ForLoopStatement(
            body=[AssignmentStatement(
                left_term=VariableExpression("a", [VariableExpression("j")]),
                right_term=Expression([
                    GroupingExpression([
                        wrong,
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
        res, error = LamportForLoopChecker().check(outer_loop)
        assert not res
        assert error == f"Variable expression ({str(wrong)}) has incorrect indexes!"

    def test_not_supported_index_operator(self):
        wrong = VariableExpression(
            "a", [Expression([VariableExpression("i"), ConstantExpression(2)], ["/"])])
        loop = ForLoopStatement(
            body=[AssignmentStatement(VariableExpression("a", [VariableExpression("i")]),
                                      wrong)],
            index=VariableExpression("i"),
            lowerbound=ConstantExpression(1),
            upperbound=VariableExpression("N")
        )
        res, error = LamportForLoopChecker().check(loop)
        assert not res
        assert error == f"Variable expression ({str(wrong)}) has incorrect indexes!"

    def test_different_variable_indexes_order(self):
        ajk = VariableExpression("a", [
            VariableExpression("j"),
            VariableExpression("k")
        ])
        akminus1k = VariableExpression("a", [
            Expression([VariableExpression("k"),
                        ConstantExpression(1)], ["-"]),
            VariableExpression("j")
        ])
        ajminus1kminus1 = VariableExpression("a", [
            Expression([VariableExpression("j"),
                        ConstantExpression(1)], ["-"]),
            Expression([VariableExpression("k"),
                        ConstantExpression(1)], ["-"]),
        ])

        right = Expression([
            ajk, akminus1k, ajminus1kminus1
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

        res, error = LamportForLoopChecker().check(iloop)
        assert not res
        assert error == f"Variable expressions ({str(ajk)}) and ({str(akminus1k)}) have the same name but different indexes order!"
