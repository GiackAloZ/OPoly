from abc import ABC, abstractmethod

from opoly.statements import Statement, ForLoopStatement, AssignmentStatement, divide_assignments, prune_expressions
from opoly.expressions import (
    Expression,
    ConstantExpression,
    VariableExpression,
    extract_variable_expressions,
    divide_variable_expressions_by_name
)


def is_simple_variable_sum_with_positive_constant(expr: Expression) -> bool:
    if (len(expr.operators) == 1 and
        (expr.operators[0] == "+" or expr.operators[0] == "-") and
        len(expr.terms) == 2
        ):
        if expr.terms[0].is_variable():
            return expr.terms[0].is_simple() and expr.terms[1].is_constant()
    return False

def get_simple_variable_sum_and_constant(expr: Expression) -> (VariableExpression, ConstantExpression):
    return expr.terms[0], ConstantExpression(expr.terms[1].value * (-1 if expr.operators[0] == "-" else 1))

def is_perfectly_nested_loop(loop: ForLoopStatement) -> bool:
    if len(loop.body) > 1:
        return not any([isinstance(st, ForLoopStatement) for st in loop.body])
    if isinstance(loop.body[0], ForLoopStatement):
        return is_perfectly_nested_loop(loop.body[0])
    return True


def get_inner_loop_statements(loop: ForLoopStatement) -> tuple[Statement]:
    if len(loop.body) == 1 and isinstance(loop.body[0], ForLoopStatement):
        return get_inner_loop_statements(loop.body[0])
    return loop.body


def is_plain_loop(loop: ForLoopStatement) -> bool:
    return ((loop.lowerbound.is_constant() and loop.lowerbound.value >= 0) and
            (((loop.upperbound.is_variable() and loop.upperbound.is_simple()) or
              is_simple_variable_sum_with_positive_constant(loop.upperbound))) and
            loop.step.is_constant() and loop.step.value == 1
            )


def is_recursively_plain_loop(loop: ForLoopStatement) -> bool:
    return is_plain_loop(loop) and all(
        map(
            lambda l: is_recursively_plain_loop(l),
            filter(lambda l: isinstance(l, ForLoopStatement), loop.body)
        )
    )


def get_indexed_variable_simple_indexes(var: VariableExpression) -> tuple[VariableExpression]:
    indexes = []
    for idx in var.indexes:
        if idx.is_variable() and idx.is_simple():
            indexes.append(idx)
        elif is_simple_variable_sum_with_positive_constant(idx):
            indexes.append(idx.terms[0])
        else:
            return None
    return indexes


def get_indexed_variable_index_constants(var: VariableExpression) -> tuple[ConstantExpression]:
    constants = []
    for idx in var.indexes:
        if idx.is_variable() and idx.is_simple():
            constants.append(ConstantExpression(0))
        elif is_simple_variable_sum_with_positive_constant(idx):
            constants.append(idx.terms[1])
        else:
            return None
    return constants


def get_indexed_variable_index_constants_with_sign(var: VariableExpression) -> tuple[ConstantExpression]:
    constants = []
    for idx in var.indexes:
        if idx.is_variable() and idx.is_simple():
            constants.append(ConstantExpression(0))
        elif is_simple_variable_sum_with_positive_constant(idx):
            constants.append(ConstantExpression(
                    idx.terms[1].value * (-1 if idx.operators[0] == "-" else 1)))
        else:
            return None
    return constants


def extract_loop_indexes(loop: ForLoopStatement) -> tuple[VariableExpression]:
    inner_indexes = []
    if isinstance(loop.body[0], ForLoopStatement):
        inner_indexes = extract_loop_indexes(loop.body[0])
    return tuple([loop.index] + list(inner_indexes))

def extract_loop_bounds(loop: ForLoopStatement) -> tuple[(Expression, Expression)]:
    inner_bounds = []
    if isinstance(loop.body[0], ForLoopStatement):
        inner_bounds = extract_loop_bounds(loop.body[0])
    return tuple([(loop.lowerbound, loop.upperbound)] + list(inner_bounds))


def has_same_simple_indexes(var1: VariableExpression, var2: VariableExpression) -> bool:
    var1_indexes = get_indexed_variable_simple_indexes(var1)
    var2_indexes = get_indexed_variable_simple_indexes(var2)
    return var1_indexes is not None and var2_indexes is not None and \
        list(idx.name for idx in var1_indexes) == list(
            idx.name for idx in var2_indexes)


class ForLoopChecker(ABC):

    def __init__(self, **params):
        self._params_dict = params

    @abstractmethod
    def check(self, loop: ForLoopStatement) -> (bool, str):
        pass


class LamportForLoopChecker(ForLoopChecker):

    def check(self, loop: ForLoopStatement) -> (bool, str):
        if not is_perfectly_nested_loop(loop):
            return False, "Not perfectly nested loop!"
        if not is_recursively_plain_loop(loop):
            return False, "Not plain loop!"
        indexes = extract_loop_indexes(loop)
        if not all(map(lambda i: i.is_simple(), indexes)):
            return False, "Loop indexes are not simple!"
        index_names = tuple([i.name for i in indexes])  # pylint: disable=no-member
        if not len(set(index_names)) == len(index_names):
            return False, "Not all index names in loop are distinct!"
        inner_statements = get_inner_loop_statements(loop)
        if not all(map(lambda stmt: isinstance(stmt, AssignmentStatement), inner_statements)):
            return False, "Not all statements in loop body are assignments!"
        lefts, rights = divide_assignments(inner_statements)
        if not all(map(lambda l: l.is_variable(), lefts)):
            return False, "Not all left sides of statements in loop body are variable expressions!"
        generations, uses = prune_expressions(lefts, rights)
        if any(map(lambda gen: gen.is_simple(), generations)):
            return False, "All variable generations must be non-simple!"
        all_variables = tuple(list(generations) + list(uses))
        all_variables_by_name = divide_variable_expressions_by_name(
            all_variables)
        for _, same_name_vars in all_variables_by_name.items():
            all_simple = all(map(lambda v: v.is_simple(), same_name_vars))
            all_non_simple = all(
                map(lambda v: not v.is_simple(), same_name_vars))
            if not (all_simple or all_non_simple):
                return False, "Same name variables must be all simple or all non-simple!"
        # Filter non-simple uses
        uses = tuple(filter(lambda use: not use.is_simple(), uses))
        all_variables = tuple(list(generations) + list(uses))

        # Check variable indexes
        var_names_dict = divide_variable_expressions_by_name(all_variables)
        for _, same_name_vars in var_names_dict.items():
            for var1 in same_name_vars:
                var1_indexes = get_indexed_variable_simple_indexes(var1)
                var1_constants = get_indexed_variable_index_constants(var1)
                if var1_indexes is None or var1_constants is None:
                    return False, f"Variable expression ({str(var1)}) has incorrect indexes!"
                var1_index_names = tuple([i.name for i in var1_indexes])

                if not all(map(lambda i: i.name in index_names, var1_indexes)):
                    return False, f"Variable expression ({str(var1)}) has an index not present in loop indexes!"
                if not len(set(var1_index_names)) == len(var1_index_names):
                    return False, f"Variable expression ({str(var1)}) indexes are not unique!"
                if not all(map(lambda iname: iname in var1_index_names, index_names[1:])):
                    return False, f"Variable expression ({str(var1)}) has a missing index which is not ({index_names[0]})!"
                if not all(map(lambda con: isinstance(con.value, int), var1_constants)):
                    return False, f"Variable expression ({str(var1)}) has a non-integer constant in one of the indexes!"

            for var1 in same_name_vars:
                for var2 in same_name_vars:
                    if not has_same_simple_indexes(var1, var2):
                        return False, f"Variable expressions ({str(var1)}) and ({str(var2)}) have the same name but different indexes order!"
        return (True, None)
