import numpy as np
import sympy as sp
from sympy.solvers.inequalities import reduce_inequalities

from opoly.expressions import ConstantExpression, VariableExpression
from opoly.statements import ForLoopStatement
from opoly.modules.checker import (
    extract_loop_indexes,
    extract_loop_bounds,
    get_simple_variable_sum_and_constant,
    get_inner_loop_statements
)
from opoly.modules.parser import parse_expression

def reduce_ineq(
    ineq: sp.core.relational._Inequality,
    var: sp.core.symbol.Symbol
) -> sp.core.relational._Inequality:
    interval = reduce_inequalities(ineq, [var])
    args = interval.args if isinstance(interval, sp.And) else [interval]
    for inter in args:
        if not inter.lhs.has(var):
            inter = inter.canonical
        if not (inter.has(sp.oo) or inter.has(-sp.oo)):
            return inter


def fourier_motzkin_eliminate_var(
    inequalites: tuple[sp.core.relational._Inequality],
    var: sp.core.symbol.Symbol,
    all_vars: tuple[sp.core.symbol.Symbol]
) -> tuple[sp.core.relational._Inequality]:
    less_exprs = []
    great_exprs = []
    zero_ineqs = []
    for ineq in inequalites:
        if var in ineq.free_symbols:
            ineq = reduce_ineq(ineq, var)
            if isinstance(ineq, sp.core.relational.GreaterThan):
                great_exprs.append(ineq.rhs)
            else:
                less_exprs.append(ineq.rhs)
        else:
            zero_ineqs.append(ineq)
    new_ineqs = []
    for ge in great_exprs:
        for le in less_exprs:
            diff = ge - le
            if any(diff.has(v) for v in all_vars):
                new_ineqs.append(ge <= le)
    return tuple(zero_ineqs + new_ineqs)


def extract_var_bounds(
    ineqs: tuple[sp.core.relational._Inequality],
    var: sp.core.symbol.Symbol
) -> (tuple[sp.core.expr.Expr], tuple[sp.core.expr.Expr]):
    lower_bounds = []
    upper_bounds = []
    for ineq in ineqs:
        if var in ineq.free_symbols:
            ineq = reduce_ineq(ineq, var)
            if ineq.has(var):
                bound = sp.together(ineq.rhs)
                if isinstance(ineq, sp.core.relational.GreaterThan):
                    lower_bounds.append(bound)
                else:
                    upper_bounds.append(bound)
    return (tuple(lower_bounds), tuple(upper_bounds))


def fourier_motzkin(
    ineqs: tuple[sp.core.relational._Inequality],
    all_vars: tuple[sp.core.symbol.Symbol],
    last_index: int = 0
) -> dict[sp.core.symbol.Symbol, (tuple[sp.core.expr.Expr], tuple[sp.core.expr.Expr])]:
    dim = len(all_vars)
    bounds_dict = {}
    curr_index = dim - 1

    while curr_index > last_index:
        curr_var = all_vars[curr_index]
        bounds_dict[curr_var] = extract_var_bounds(ineqs, curr_var)
        ineqs = fourier_motzkin_eliminate_var(ineqs, curr_var, all_vars)
        curr_index -= 1

    last_var = all_vars[last_index]
    bounds_dict[last_var] = extract_var_bounds(ineqs, last_var)
    return bounds_dict


def enclose_bounds(
    bounds_dict: dict[sp.core.symbol.Symbol,
                      (tuple[sp.core.expr.Expr], tuple[sp.core.expr.Expr])]
) -> dict[sp.core.symbol.Symbol, (tuple[sp.core.expr.Expr], tuple[sp.core.expr.Expr])]:
    enclosed_bounds_dict = {}
    for var, bounds in bounds_dict.items():
        lowers, uppers = bounds
        ceiled_lowers = map(lambda l: sp.ceiling(l)
                            if isinstance(l, sp.core.mul.Mul) and
                            any(map(lambda l: l.is_rational and not l.is_integer, l.as_two_terms())) else l, lowers)
        floored_uppers = map(lambda l: sp.floor(l)
                             if isinstance(l, sp.core.mul.Mul) and
                             any(map(lambda l: l.is_rational and
                                     not l.is_integer, l.as_two_terms()))
                             else l,
                             uppers)
        enclosed_bounds_dict[var] = (
            sp.Max(*ceiled_lowers),
            sp.Min(*floored_uppers)
        )
    return enclosed_bounds_dict


def reindex(T_inv: np.array, x: sp.Matrix, ls: sp.Matrix, us: sp.Matrix):
    system = T_inv * x
    ineqs = []
    for i, t in enumerate(system):
        ineqs.append(t >= ls[i])
        ineqs.append(t <= us[i])
    all_vars = tuple(xx for xx in x)
    bounds = fourier_motzkin(ineqs, all_vars)
    return enclose_bounds(bounds)

def invert_integer_matrix(mat: np.ndarray):
    return np.linalg.inv(mat).round().astype(np.int)

class LamportReindexer():

    def extract_bounds(self, bounds):
        res = []
        for b in bounds:
            if b.is_constant():
                res.append(b.value)
            elif b.is_variable():
                res.append(sp.var(b.name))
            else:
                v, c = get_simple_variable_sum_and_constant(b)
                res.append(sp.var(v.name) + c.value)
        return sp.Matrix(res)

    def reindex(self, loop: ForLoopStatement, allocation: np.ndarray) -> ForLoopStatement:
        indexes = sp.Matrix(list(
            [sp.var(i.name) for i in extract_loop_indexes(loop)] # pylint: disable=no-member
        ))
        lower_bounds, upper_bounds = list(zip(*extract_loop_bounds(loop)))
        ls = self.extract_bounds(lower_bounds)
        us = self.extract_bounds(upper_bounds)
        new_bounds = reindex(
            invert_integer_matrix(allocation),
            indexes,
            ls,
            us
        )
        statements = get_inner_loop_statements(loop)
        last_loop = None

        for i in reversed(indexes):
            lb, _ = parse_expression(sp.ccode(new_bounds[i][0]))
            ub, _ = parse_expression(sp.ccode(new_bounds[i][1]))

            if last_loop is None:
                body = statements
            else:
                body = [last_loop]
            
            last_loop = ForLoopStatement(
                body=body,
                index=VariableExpression(repr(i)),
                lowerbound=lb,
                upperbound=ub
            )
        return last_loop
