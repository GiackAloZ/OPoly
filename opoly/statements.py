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
    DECLARATION = auto()
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

class SimpleStatement(Statement, ABC):

    def __init__(self, stype: StatementType):
        super().__init__(stype)

class AssignmentStatement(SimpleStatement):

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


class DeclarationStatement(SimpleStatement):
    def __init__(self, var_type: str, variable: VariableExpression, initialization: Expression = None):
        super().__init__(StatementType.DECLARATION)
        self._var_type = var_type
        self._variable = variable
        self._initialization = initialization

    @property
    def var_type(self) -> str:
        return self._var_type

    @property
    def variable(self) -> VariableExpression:
        return self._variable

    @property
    def initialization(self) -> Expression:
        return self._initialization

    def stringify(self) -> str:
        decl_str = f"{self.var_type} {str(self.variable)}"
        init_str = f" = {str(self.initialization)}" if self.initialization is not None else ""
        return f"{decl_str}{init_str}"


class CompoundStatement(Statement, ABC):

    def __init__(self, stype: StatementType, body: tuple[Statement]):
        super().__init__(stype)
        if len(body) == 0:
            raise ValueError("Compound statement body cannot be empty!")
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


class ForLoopStatement(CompoundStatement):

    def __init__(self,
                 body: tuple[Statement],
                 index: VariableExpression,
                 lowerbound: Expression,
                 upperbound: Expression,
                 step: Expression = ConstantExpression(1),
                 is_parallel: bool = False
                 ):
        super().__init__(StatementType.FOR_LOOP, body)
        self._index = index
        self._lowerbound = lowerbound
        self._upperbound = upperbound
        self._step = step
        self._is_parallel = is_parallel

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
    
    @property
    def is_parallel(self) -> bool:
        return self._is_parallel

    def stringify_head(self) -> str:
        head = f"FOR {self.index} = {self.lowerbound}...{self.upperbound}"
        step = "" if isinstance(self.step, ConstantExpression) or self.step.value == 1 \
            else f" step {self.step}"
        return f"{head}{step}"


def divide_assignments(
    assignments: tuple[AssignmentStatement]
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
