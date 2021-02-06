from abc import ABC, abstractmethod
import re

from opoly.expressions import Expression, ConstantExpression, VariableExpression, GroupingExpression
from opoly.statements import Statement, ForLoopStatement, AssignmentStatement


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
    supported_operators = [
        "+", "-", "*", "/"
    ]
    if code[0] not in supported_operators:
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


def parse_expression(code: str, term_char=None) -> (Expression, str):
    terms = []
    operators = []
    while True:
        # Check for expression
        if len(code) == 0:
            return None, "Expected expression"

        # Check different subexpression terms
        if code[0].isalpha():
            next_term, code = parse_variable_expression(code.strip())
        elif code[0].isnumeric():
            next_term, code = parse_constant_expression(code.strip())
        elif code[0] == "(":
            next_term, code = parse_grouping_expression(code.strip())
        else:
            return None, "Unsupported expression term"
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
        r"^VAR\s+(?P<ass>.*?\s*=\s*.*?);"
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
                code = code[end:]
                body_stmts.append(stmt)
                continue

            match = self.ASSIGNMENT_REGEX.match(code)
            if match is not None:
                start, end = match.span()
                assignment_code = match.groupdict()["ass"].strip()
                stmt, err = parse_assignment_statement(assignment_code)
                if stmt is None:
                    return None, err
                code = code[end+1:]
                body_stmts.append(stmt)
                continue

            return None, "Unsupported statement"
        return body_stmts, None

    def parse_for_loop(self, code: str) -> (ForLoopStatement, str):
        code = code.strip().replace("\n", " ")
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
