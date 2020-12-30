from abc import ABC, abstractmethod
from enum import auto, Enum

from opoly.expressions import Expression, VariableExpression


class StatementType(Enum):
    FOR_LOOP = auto()
    ASSIGNMENT = auto()


class Statement(ABC):

    def __init__(self, stm_type: StatementType):
        self._stm_type = stm_type

    @property
    def stm_type(self) -> StatementType:
        return self._stm_type

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

    def __init__(self, stm_type: StatementType, body: list[Statement]):
        super().__init__(stm_type)
        self._body = body

    @property
    def body(self) -> list[Statement]:
        return self._body

    @abstractmethod
    def stringify_head(self) -> str:
        pass

    def stringify(self) -> str:
        head = self.stringify_head()
        body = "\n".join([f"\t{s}" for s in self.body])
        return "\n".join([head, body])


class ForLoopStatement(BlockStatement):

    def __init__(self,
                 body: list[Statement],
                 index: str,
                 lb: int or str,
                 ub: int or str,
                 step: int = 1
                 ):
        super().__init__(StatementType.FOR_LOOP, body)
        self._index = index
        self._lb = lb
        self._ub = ub
        if step == 0:
            raise ValueError("Step size cannot be zero!")
        self._step = step

    @property
    def index(self) -> str:
        return self._index

    @property
    def lb(self) -> int or str:
        return self._lb

    @property
    def ub(self) -> int or str:
        return self._ub

    @property
    def step(self) -> int or str:
        return self._step

    def stringify_head(self) -> str:
        return f"FOR {self.index} = {self.lb}...{self.ub}{f' step {self.step}' if self.step != 1 else ''}"
