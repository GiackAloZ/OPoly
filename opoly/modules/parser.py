from abc import ABC, abstractmethod
import re

from opoly.expressions import (
    Expression, ConstantExpression, VariableExpression, GroupingExpression, FunctionExpression, UnaryExpression)
from opoly.statements import Statement, ForLoopStatement, AssignmentStatement

FUNCTION_EXPRESSION_REGEX = re.compile(r"^(?P<name>\w+)\((?P<terms>.*)\)")
FUNCTION_TERMS_EXPRESSION_REGEX = re.compile(r"^(?P<term>[^,\s].*?)(,|$)")
UNARY_OPERATORS = [
    "-"
]
BINARY_OPERATORS = [
    "+", "-", "*", "/"
]


def isfloat(s: str) -> bool:
    try:
        _ = float(s)
    except (TypeError, ValueError):
        return False
    else:
        return True


def isint(s: str):
    try:
        _ = int(s)
    except (TypeError, ValueError):
        return False
    else:
        return True

# TODO fix every return value with Optional[]


def parse_constant_expression(code: str) -> (ConstantExpression, str):
    if len(code) == 0:
        return None, "Expected constant expression"
    i = 0
    while i < len(code) and (code[i].isnumeric() or code[i] == "."):
        i += 1
    res_str = code[:i]
    if isint(res_str):
        res = int(res_str)
    elif isfloat(res_str):
        res = float(res_str)
    else:
        return None, "Expected constant expression"
    return ConstantExpression(res), code[i:]


def parse_variable_expression(code: str) -> (VariableExpression, str):
    if len(code) == 0:
        return None, "Expected variable expression"
    i = 0
    while i < len(code) and (code[i].isalpha() or code[i] == "_"):
        i += 1
    name = code[:i]
    if name == "":
        return None, "Expected variable expression"
    code = code[i:]
    indexes = []
    while len(code) > 0 and code[0] == "[":
        var_index, rem_code = parse_expression(code[1:].strip(), term_char="]")
        if var_index is None:
            return None, rem_code
        rem_code = rem_code.strip()
        if len(rem_code) == 0 or rem_code[0] != "]":
            return None, "Expected ]"
        indexes.append(var_index)
        code = rem_code[1:]
    return VariableExpression(name, indexes), code


def parse_operator(code: str) -> (str, str):
    if len(code) == 0:
        return None, "Expected operator"
    if code[0] not in BINARY_OPERATORS:
        return None, "Unsupported operator"
    return code[0], code[1:]


def parse_grouping_expression(code: str) -> (GroupingExpression, str):
    if len(code) == 0 or code[0] != "(":
        return None, "Expected ("
    expr, rem_code = parse_expression(code[1:], term_char=")")
    if expr is None:
        return None, rem_code
    rem_code = rem_code.strip()
    if len(rem_code) == 0 or rem_code[0] != ")":
        return None, "Expected )"
    return GroupingExpression([expr], []), rem_code[1:]


def parse_simple_function_expression(code: str) -> (FunctionExpression, str):
    match = FUNCTION_EXPRESSION_REGEX.match(code)
    if not match:
        return None, "Expected function expression"
    name = match.group("name")
    terms_code = match.group("terms").strip()
    terms = []
    while (term_match := FUNCTION_TERMS_EXPRESSION_REGEX.match(terms_code)) is not None:
        term, err = parse_expression(term_match.group("term").strip())
        if term is None:
            return None, err
        terms_code = terms_code[term_match.span()[1]:].strip()
        terms.append(term)
    if len(terms_code) != 0:
        return None, "Function expression not well formatted"
    return FunctionExpression(name, args=terms), code[match.span()[1]:]

def parse_function_expression(code: str) -> (FunctionExpression, str):
    if len(code) == 0:
        return None, "Expected function expression"
    i = 0
    while i < len(code) and (code[i].isalpha() or code[i] == "_"):
        i += 1
    name = code[:i]
    if name == "":
        return None, "Expected function name"
    code = code[i:]
    if len(code) == 0 or code[0] != "(":
        return None, "Expected ("
    expressions = []
    while True:
        expr, rem_code = parse_expression(code[1:], term_char=",")
        if expr is None:
            break
        rem_code = rem_code.strip()
        if len(rem_code) == 0 or rem_code[0] != ",":
            return None, "Expected ,"
        code = rem_code
        expressions.append(expr)
        
    last_expr, rem_code = parse_expression(code[1:], term_char=")")
    if last_expr is None:
        return None, rem_code
    expressions.append(last_expr)
    rem_code = rem_code.strip()
    if len(rem_code) == 0 or rem_code[0] != ")":
        return None, "Expected )"
    return FunctionExpression(name, tuple(expressions)), rem_code[1:]

def parse_unary_expression(code: str) -> (UnaryExpression, str):
    if len(code) == 0:
        return None, "Expected unary expression"
    if code[0] not in UNARY_OPERATORS:
        return None, "Unsupported unary operator"
    if parse_unary_expression(code[1:].strip())[0] is not None:
        return None, "Unsupported unary operator"
    term, rem_code = parse_single_expression(code[1:].strip())
    if term is None:
        return None, rem_code
    return UnaryExpression(term, code[0]), rem_code

def parse_single_expression(code: str) -> (Expression, str):
    code = code.strip()
    # Check for expression
    if len(code) == 0:
        return None, "Expected expression"

    # Check different subexpression terms
    if FUNCTION_EXPRESSION_REGEX.match(code) is not None:
        next_term, code = parse_function_expression(code)
    elif code[0].isalpha():
        next_term, code = parse_variable_expression(code)
    elif code[0].isnumeric():
        next_term, code = parse_constant_expression(code)
    elif code[0] == "(":
        next_term, code = parse_grouping_expression(code)
    elif code[0] in UNARY_OPERATORS:
        next_term, code = parse_unary_expression(code)
    else:
        return None, "Unsupported expression term"
    return next_term, code

def parse_expression(code: str, term_char=None) -> (Expression, str):
    terms = []
    operators = []
    while True:
        # Parse next expression
        next_term, code = parse_single_expression(code)
        if next_term is None:
            return None, code
        terms.append(next_term)

        # Check for end
        code = code.strip()
        if len(code) == 0:
            break

        # Check for operator
        next_operator, rem_code = parse_operator(code)
        if next_operator is not None:
            operators.append(next_operator)
            code = rem_code.strip()
            continue
        if next_operator is None and term_char is not None and code[0] != term_char and term_char in code:
            return None, rem_code

        # Check for term char
        if term_char is not None:
            if code[0] == term_char:
                break
            return None, f"Expected {term_char}"

        return None, rem_code
    if len(terms) == 1:
        return terms[0], code
    return Expression(terms, operators), code


def parse_assignment_statement(code: str) -> (AssignmentStatement, str):
    left, *more = code.split("=")
    if len(more) == 0:
        return None, "Expected = operator"
    if len(more) > 1:
        return None, "Expected only one = operator in assignment"
    right = more[0]
    left_expr, rem = parse_variable_expression(left.strip())
    if left_expr is None:
        return None, rem
    if len(rem) > 0:
        return None, "Expected only one variable expression for left term"
    right_expr, rem = parse_expression(right.strip())
    if right_expr is None:
        return None, rem
    return AssignmentStatement(left_expr, right_expr), None


class ForLoopParser(ABC):

    @abstractmethod
    def parse_for_loop(self, code: str) -> (ForLoopStatement, str):
        pass


class PseudocodeForLoopParser(ABC):

    HEADER_REGEX = re.compile(
        r"^FOR\s+(?P<idx>.+?)\s+FROM\s+(?P<lb>.+?)\s+TO\s+(?P<ub>.+?)(?:\s+STEP\s+(?P<step>.+?))?\s*\{\s*(?P<body>.*)\s*\}"
    )

    ASSIGNMENT_REGEX = re.compile(
        r"^STM\s+(?P<ass>.*?\s*=\s*.*?);.*"
    )

    def parse_loop_body(self, code: str) -> (tuple[Statement], str):
        code = code.strip()
        body_stmts = []
        while len(code) > 0:
            match = self.HEADER_REGEX.match(code)
            if match is not None:
                start, end = match.span()
                stmt, err = self.parse_for_loop(code[start:end])
                if stmt is None:
                    return None, err
                code = code[end:].strip()
                body_stmts.append(stmt)
                continue

            match = self.ASSIGNMENT_REGEX.match(code)
            if match is not None:
                assignment_code = match.group("ass").strip()
                stmt, err = parse_assignment_statement(assignment_code)
                if stmt is None:
                    return None, err
                end_of_assigment = match.span("ass")[1]+1
                code = code[end_of_assigment:].strip()
                body_stmts.append(stmt)
            else:
                return None, f"Unsupported statement: {code}"
        return body_stmts, None

    def parse_for_loop(self, code: str) -> (ForLoopStatement, str):
        code = re.sub(r"\s+", " ", code.strip())
        # Parse header
        if len(code) == 0:
            return None, "Expected loop header"
        match = self.HEADER_REGEX.match(code)
        if match is None:
            return None, "Incorrect loop header syntax"

        # Parse header parameters
        groups_dict = match.groupdict()
        idx_str = groups_dict["idx"]
        lb_str = groups_dict["lb"]
        ub_str = groups_dict["ub"]
        step_str = groups_dict["step"]
        idx_var_expr, err = parse_variable_expression(idx_str)
        if idx_var_expr is None:
            return None, err
        lb_expr, err = parse_expression(lb_str)
        if lb_expr is None:
            return None, err
        ub_expr, err = parse_expression(ub_str)
        if ub_expr is None:
            return None, err
        step_expr = None
        if step_str is not None:
            step_expr, err = parse_expression(step_str)
            if step_expr is None:
                return None, err

        # Parse body
        body_str = groups_dict["body"].strip()
        if body_str is None or len(body_str) == 0:
            return None, "Expected loop body"
        body, err = self.parse_loop_body(body_str)
        if body is None:
            return None, err

        if step_expr is not None:
            return ForLoopStatement(
                body=body,
                index=idx_var_expr,
                lowerbound=lb_expr,
                upperbound=ub_expr,
                step=step_expr
            ), None
        return ForLoopStatement(
            body=body,
            index=idx_var_expr,
            lowerbound=lb_expr,
            upperbound=ub_expr
        ), None
