from .visitor import Visitor
from .ast import Scope
from .standard_library import StandardLibrary
from .qasm import *


# A Transpiler converts an AST into OpenQASM programs by visiting the nodes
# and converting.
class Transpiler(Visitor):
    def __init__(self, ast):
        ast.go_to_top()
        super().__init__(ast.context)
        self.regions = {}
        self.functions = {}

    def visit_function(self, func):
        # Add a new function to the definitions table
        name = func.get_name().name
        measured = func.get_type().measured
        instructions = self.convert_to_instructions(func.get_block())
        self.functions[name] = (measured, instructions)

    def convert_to_instructions(self, stmt: Scope) -> list:
        if stmt.data == "block":
            return [self.convert_to_instructions(s) for s in stmt.children]
        elif stmt.data == "function_call":
            # Is this in the standard library?
            if StandardLibrary.is_standard(stmt.get_name().name):
                return StandardLibrary.generate_instruction_for(stmt.get_name().name, stmt.get_classical_arguments(), stmt.get_quantum_arguments())
            else:
                return [FunctionCall(stmt.get_name().name, stmt.get_classical_arguments(), stmt.get_quantum_arguments())]

class OpenQASMProgram:
    def __init__(self, instructions, gates):
        self.instructions = instructions
        self.gates = gates


class OpenQASMGate:
    def __init__(self, instructions):
        self.instructions = instructions