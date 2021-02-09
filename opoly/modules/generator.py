from abc import ABC, abstractmethod

from opoly.statements import Statement, StatementType, ForLoopStatement, DeclarationStatement, AssignmentStatement


class CodeGenerator(ABC):

    @abstractmethod
    def generate(self, stmt: Statement) -> str:
        pass


class PseudoCodeGenerator(CodeGenerator):

    INDENTATION_SPACES = " " * 4

    def generate_for_loop(self, stmt: ForLoopStatement, level=0) -> str:
        head = f"FOR {stmt.index} FROM {stmt.lowerbound} TO {stmt.upperbound} STEP {stmt.step} " + "{\n"
        body = f"\n".join([self.generate(t, level=level+1) for t in stmt.body])
        return (self.INDENTATION_SPACES * level) + head + body + "\n" + (self.INDENTATION_SPACES * level) + "}"

    def generate_declaration(self, stmt: DeclarationStatement, level=0) -> str:
        head = f"VAR {stmt.variable}"
        init_str = f" = {stmt.initialization}" if stmt.initialization is not None else ""
        return (self.INDENTATION_SPACES * level) + head + init_str + ";"

    def generate_assignment(self, stmt: AssignmentStatement, level=0) -> str:
        return (self.INDENTATION_SPACES * level) + f"STM {stmt.left_term} = {stmt.right_term};"

    def generate(self, stmt: Statement, level=0) -> str:
        if stmt.stype == StatementType.FOR_LOOP:
            return self.generate_for_loop(stmt, level=level)
        if stmt.stype == StatementType.DECLARATION:
            return self.generate_declaration(stmt, level=level)
        if stmt.stype == StatementType.ASSIGNMENT:
            return self.generate_assignment(stmt, level=level)
        return None

class CCodeGenerator(CodeGenerator):

    INDENTATION_SPACES = " " * 4

    def generate_for_loop(self, stmt: ForLoopStatement, level=0) -> str:
        head = f"for(int {stmt.index} = {stmt.lowerbound}; {stmt.index} <= {stmt.upperbound}; {stmt.index} += {stmt.step}) " + "{\n"
        body = f"\n".join([self.generate(t, level=level+1) for t in stmt.body])
        return (self.INDENTATION_SPACES * level) + head + body + "\n" + (self.INDENTATION_SPACES * level) + "}"

    def generate_declaration(self, stmt: DeclarationStatement, level=0) -> str:
        head = f"{stmt.var_type} {stmt.variable}"
        init_str = f" = {stmt.initialization}" if stmt.initialization is not None else ""
        return (self.INDENTATION_SPACES * level) + head + init_str + ";"

    def generate_assignment(self, stmt: AssignmentStatement, level=0) -> str:
        return (self.INDENTATION_SPACES * level) + f"{stmt.left_term} = {stmt.right_term};"

    def generate(self, stmt: Statement, level=0) -> str:
        if stmt.stype == StatementType.FOR_LOOP:
            return self.generate_for_loop(stmt, level=level)
        if stmt.stype == StatementType.DECLARATION:
            return self.generate_declaration(stmt, level=level)
        if stmt.stype == StatementType.ASSIGNMENT:
            return self.generate_assignment(stmt, level=level)
        return None
