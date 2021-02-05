from opoly.expressions import ConstantExpression

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
    i = 0
    while i < len(code) and (code[i].isnumeric() or code[i] == "."):
        i += 1
    res_str = code[:i]
    if isint(res_str):
        res = int(res_str)
    elif isfloat(res_str):
        res = float(res_str)
    else:
        return None, code
    return ConstantExpression(res), code[i:]