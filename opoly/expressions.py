from __future__ import annotations


class Expression():

    def __init__(self,
                 terms: list[Expression],
                 operators: list[str]
                 ):
        if len(terms) == 0:
            raise ValueError(
                "There must be at least one term in the expression!")
        self._terms = terms
        if len(terms) - 1 != len(operators):
            raise ValueError(
                "Number of operators must be the number of terms minus one!")
        self._operators = operators

    @property
    def terms(self) -> list[Expression]:
        return self._terms

    @property
    def operators(self) -> list[str]:
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

class ConstantExpression(Expression):

    def __init__(self, value: str):
        super().__init__([self], [])
        self._value = value
    
    @property
    def value(self) -> str:
        return self._value
    
    def stringify(self) -> str:
        return self.value

class VariableExpression(Expression):

    # TODO fix with Optional
    def __init__(self, name: str, indexes: list[Expression] = []):
        super().__init__([self], [])
        self._name = name
        self._indexes = indexes

    @property
    def name(self) -> str:
        return self._name

    @property
    def indexes(self) -> list[str]:
        return self._indexes

    def stringify(self) -> str:
        return f"{self.name}{''.join([f'[{i}]' for i in self.indexes])}"
