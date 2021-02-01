from abc import ABC, abstractmethod
from enum import auto, Enum

from collections import Counter

from opoly.expressions import (
    Expression,
    SingleExpression,
    VariableExpression,
    ConstantExpression,
    extract_variable_expressions
)


class StatementType(Enum):
    FOR_LOOP = auto()
    ASSIGNMENT = auto()


class Statement(ABC):

    def __init__(self, stype: StatementType):
        self._stype = stype

    @property
    def stype(self) -> StatementType:
        return self._stype

    @abstractmethod
    def stringify(self) -> str:
        pass

    def __str__(self):
        return self.stringify()


class AssigmentStatement(Statement):
    def __init__(self, left_term: VariableExpression, right_term: Expression):
        super().__init__(StatementType.ASSIGNMENT)
        self._left_term = left_term
        self._right_term = right_term

    @property
    def left_term(self) -> VariableExpression:
        return self._left_term

    @property
    def right_term(self) -> Expression:
        return self._right_term

    def stringify(self) -> str:
        return f"{self.left_term} = {self.right_term}"


class BlockStatement(Statement, ABC):

    def __init__(self, stype: StatementType, body: tuple[Statement]):
        super().__init__(stype)
        if len(body) == 0:
            raise ValueError("Block statement body cannot be empty!")
        self._body = body

    @property
    def body(self) -> tuple[Statement]:
        return self._body

    @abstractmethod
    def stringify_head(self) -> str:
        pass

    def stringify(self) -> str:
        head = self.stringify_head()
        body = "\n".join([str(s) for s in self.body])
        return "\n".join([head, body])


class ForLoopStatement(BlockStatement):

    def __init__(self,
                 body: tuple[Statement],
                 index: VariableExpression,
                 lowerbound: Expression,
                 upperbound: Expression,
                 step: Expression = ConstantExpression(1)
                 ):
        super().__init__(StatementType.FOR_LOOP, body)
        self._index = index
        self._lowerbound = lowerbound
        self._upperbound = upperbound
        self._step = step

    @property
    def index(self) -> VariableExpression:
        return self._index

    @property
    def lowerbound(self) -> Expression:
        return self._lowerbound

    @property
    def upperbound(self) -> Expression:
        return self._upperbound

    @property
    def step(self) -> Expression:
        return self._step

    def is_plain(self) -> bool:
        return self.index.is_simple() and \
            isinstance(self.lowerbound, ConstantExpression) and \
            isinstance(self.upperbound, SingleExpression) and \
            (True if not isinstance(self.upperbound, VariableExpression)
             else self.upperbound.is_simple()) and \
            isinstance(self.step, ConstantExpression) and \
            self.step.value == 1

    def stringify_head(self) -> str:
        head = f"FOR {self.index} = {self.lowerbound}...{self.upperbound}"
        step = "" if isinstance(self.step, ConstantExpression) or self.step.value == 1 \
            else f" step {self.step}"
        return f"{head}{step}"


def check_perfectly_nested_loop(loop: ForLoopStatement) -> bool:
    if len(loop.body) > 1:
        return not any([isinstance(st, ForLoopStatement) for st in loop.body])
    if isinstance(loop.body[0], ForLoopStatement):
        return check_perfectly_nested_loop(loop.body[0])
    return True


def check_plain_nested_loop(loop: ForLoopStatement) -> bool:
    for stmt in loop.body:
        if isinstance(stmt, ForLoopStatement) and not check_plain_nested_loop(stmt):
            return False
    return loop.is_plain()


def divide_assignments(
    assignments: tuple[AssigmentStatement]
) -> (tuple[VariableExpression], tuple[VariableExpression]):
    generations = []
    uses = []
    for ass in assignments:
        generations.append(ass.left_term)
        uses.extend(extract_variable_expressions(ass.right_term))
    return (tuple(generations), tuple(uses))


def prune_expressions(
    generations: tuple[VariableExpression], uses: tuple[VariableExpression]
) -> (tuple[VariableExpression], tuple[VariableExpression]):
    gen_names = set(gen.name for gen in generations)
    use_names = set(use.name for use in uses)
    both_names = gen_names & use_names

    count_names = Counter(var.name for var in generations + uses)

    generations = filter(
        lambda g: g.name in gen_names and count_names[g.name] > 1, generations)
    uses = filter(lambda u: u.name in both_names, uses)
    return (tuple(generations), tuple(uses))
