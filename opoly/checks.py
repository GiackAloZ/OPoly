from opoly.statements import ForLoopStatement


def check_perfectly_nested_loop(loop: ForLoopStatement) -> bool:
    if len(loop.body) > 1:
        return not any([isinstance(st, ForLoopStatement) for st in loop.body])
    if isinstance(loop.body[0], ForLoopStatement):
        return check_perfectly_nested_loop(loop.body[0])
    return True
