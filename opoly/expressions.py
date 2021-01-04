from __future__ import annotations

from abc import ABC


class Expression():

    def __init__(self,
                 terms: tuple[Expression],
                 operators: tuple[str]
                 ):
        if not len(terms) > 0:
            raise ValueError(
                "There must be at least one term in the expression!")
        self._terms = terms
        if not len(terms) - 1 == len(operators):
            raise ValueError(
                "Number of operators must be the number of terms minus one!")
        self._operators = operators

    @property
    def terms(self) -> tuple[Expression]:
        return self._terms

    @property
    def operators(self) -> tuple[str]:
        return self._operators

    def is_single(self) -> bool:
        return len(self.terms) == 1

    def stringify(self) -> str:
        res = str(self.terms[0])
        for i in range(len(self.operators)):
            res += f" {self.operators[i]} {self.terms[i+1]}"
        return res

    def __str__(self):
        return self.stringify()


class GroupingExpression(Expression):

    def stringify(self) -> str:
        return f"({super().stringify()})"


class SingleExpression(Expression, ABC):

    def __init__(self):
        super().__init__((self,), ())


class ConstantExpression(SingleExpression):

    def __init__(self, value: int or float):
        super().__init__()
        self._value = value

    @property
    def value(self) -> int or float:
        return self._value

    def stringify(self) -> str:
        return str(self.value)


class VariableExpression(SingleExpression):

    # TODO fix with Optional
    def __init__(self, name: str, indexes: tuple[Expression] = ()):
        super().__init__()
        self._name = name
        self._indexes = indexes

    @property
    def name(self) -> str:
        return self._name

    @property
    def indexes(self) -> tuple[str]:
        return self._indexes

    def is_simple(self) -> bool:
        return len(self.indexes) == 0

    def stringify(self) -> str:
        return f"{self.name}{''.join([f'[{i}]' for i in self.indexes])}"


class FunctionExpression(SingleExpression):

    def __init__(self, name: str, args: tuple[Expression] = ()):
        super().__init__()
        self._name = name
        self._args = args

    @property
    def name(self) -> str:
        return self._name

    @property
    def args(self) -> tuple[Expression]:
        return self._args

    def stringify(self) -> str:
        return f"{self.name}({','.join([str(t) for t in self.args])})"
