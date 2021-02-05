from opoly.expressions import Expression, ConstantExpression, VariableExpression, GroupingExpression
from opoly.statements import ForLoopStatement, AssignmentStatement


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
