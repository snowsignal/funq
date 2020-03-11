from visitor import Visitor
from scope import Scope
from standard_library import StandardLibrary
from qasm import *


# A Transpiler converts an AST into OpenQASM programs by visiting the nodes
# and converting.
class Transpiler(Visitor):
    def __init__(self, ast):
        ast.go_to_top()
        super().__init__(ast.context)
        self.regions = {}
        self.functions = {}

    def visit_region(self, region):
        print("Visiting region")
        name = region.get_name().name
        instructions = self.convert_to_instructions(region.get_block())
        print(instructions)
        self.regions[name] = instructions

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
            cargs = stmt.get_call_list().get_classical_arguments()
            qargs = stmt.get_call_list().get_quantum_arguments()
            # Is this in the standard library?
            if StandardLibrary.is_standard(stmt.get_name().name):
                return [FunctionCall(StandardLibrary.get_standard_name(stmt.get_name().name), cargs, qargs)]
            else:
                return [FunctionCall(stmt.get_name().name, cargs, qargs)]
        elif stmt.data == "if":
            arg1, arg2 = stmt.get_args()
            op = stmt.get_op()
            arg1 = self.convert_classical_arg(arg1)
            arg2 = self.convert_classical_arg(arg2)
            comp = Comparison(arg1, arg2, op)
            sub_instructions = [self.convert_to_instructions(c) for c in stmt.get_block().children]
            return [IfInstruction(comp, sub_instructions)]
        elif stmt.data == "q_decl":
            name = stmt.get_name().name
            size = stmt.get_length()
            return [QuantumInitialization(name, size)]
        else:
            raise Exception("Unexpected statement type: " + str(stmt.__dict__))

    def convert_classical_arg(self, arg):
        if arg.type == "uint":
            return UIntArgument(arg.value)
        elif arg.type == "v_ident":
            return CRegArgument(arg.name)
        else:
            raise Exception("Unexpected argument type!")


class OpenQASMProgram:
    def __init__(self, instructions, gates):
        self.instructions = instructions
        self.gates = gates


class OpenQASMGate:
    def __init__(self, cargs, qargs, instructions):
        self.cargs = cargs
        self.qargs = qargs
        self.instructions = instructions