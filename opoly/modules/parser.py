from opoly.expressions import Expression, ConstantExpression, VariableExpression


def isfloat(s: str) -> bool:
    try:
        _ = float(s)
    except (TypeError, ValueError):
        return False
    else:
        return True


def isint(s: str):
    try:
        a = float(s)
        b = int(a)
    except (TypeError, ValueError):
        return False
    else:
        return a == b


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
        var_index, rem_code = parse_expression(code[1:].strip())
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


def parse_expression(code: str) -> (Expression, str):
    if len(code) == 0:
        return None, "Expected expression"
    terms = []
    operators = []
    while True:
        if code[0].isalpha():
            next_term, code = parse_variable_expression(code.strip())
        elif code[0].isnumeric():
            next_term, code = parse_constant_expression(code.strip())
        elif code[0] == "(":
            raise NotImplementedError()
        else:
            return None, "Unsupported expression term"
        if next_term is None:
            return None, code
        terms.append(next_term)
        code = code.strip()
        if len(code) == 0 or code[0] == "]" or code[0] == ")":
            break
        next_operator, code = parse_operator(code)
        if next_operator is None:
            return None, code
        operators.append(next_operator)
        code = code.strip()
        if len(code) == 0:
            return None, "Expected expression"
    return Expression(terms, operators), code
