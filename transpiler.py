from scope import Scope
from standard_library import StandardLibrary
from qasm import *
from state import State


# A Transpiler converts an AST into OpenQASM programs by visiting the nodes
# and converting.
class Transpiler:
    def __init__(self, state: State):
        self.regions = state.regions
        self.functions = state.functions
        self.programs = {}
        self.gates = {}

    def transpile(self):
        for name in self.functions.keys():
            f = self.functions[name]
            self.generate_gate(name, f[0], f[1], f[2])
        for name in self.regions.keys():
            r = self.regions[name]
            self.generate_program(name, r[0], r[1], r[2], r[3])

    def visit_region(self, region):
        name = region.get_name().name
        instructions = self.convert_to_instructions(region.get_block())
        self.regions[name] = instructions

    def generate_gate(self, func_name, cargs, qargs, block):
        instructions = self.convert_to_instructions(block)
        cargs = [c.get_name().name for c in cargs]
        qargs = [q.get_name().name for q in qargs]
        self.gates[func_name] = OpenQASMGate(func_name, cargs, qargs, instructions)

    def generate_program(self, name, qubits, block, measurement_qubit_needed, dependencies):
        instructions = self.convert_to_instructions(block)
        self.programs[name] = OpenQASMProgram(qubits, instructions, dependencies, measurement_qubit_needed)

    def convert_to_instructions(self, stmt: Scope) -> list:
        if stmt.data == "block":
            instructions = []
            for s in stmt.children:
                instructions += self.convert_to_instructions(s)
            return instructions
        elif stmt.data == "function_call":
            cargs = [self.convert_classical_arg(c)
                     for c in stmt.get_call_list().get_classical_arguments()]
            qargs = [self.convert_quantum_arg(q)
                     for q in stmt.get_call_list().get_quantum_arguments()]
            # Is this in the standard library?
            if StandardLibrary.is_standard(stmt.get_name().name):
                return [FunctionCall(StandardLibrary.get_standard_name(stmt.get_name().name), cargs, qargs)]
            else:
                return [FunctionCall(stmt.get_name().name, cargs, qargs)]
        elif stmt.data == "if":
            arg1, arg2 = stmt.get_args()
            op = stmt.get_op().get_operation()
            arg1 = self.convert_classical_arg(arg1)
            arg2 = self.convert_classical_arg(arg2)
            comp = Comparison(arg1, arg2, op)
            sub_instructions = self.convert_to_instructions(stmt.get_block())
            return [IfInstruction(comp, sub_instructions)]
        elif stmt.data == "q_decl":
            name = stmt.get_name().name
            size = stmt.get_length()
            bits = stmt.get_bits()
            return [QuantumInitialization(name, size, bits)]
        elif stmt.data == "c_decl":
            name = stmt.get_name().name
            size = stmt.get_length()
            bits = stmt.get_bits()
            return [ClassicalInitialization(name, size, bits)]
        elif stmt.data == "measurement":
            expr = stmt.get_q_expr()
            r_name = stmt.get_r_name().name
            q_name = expr.get_name().name
            r_start = stmt.get_r_start().value
            if expr.data == "q_index":
                q_start = expr.get_pos()
                q_end = q_start
                return [MeasurementInstruction(r_name, r_start, q_name, q_start, q_end)]
            elif expr.data == "q_slice":
                q_start, q_end = expr.get_start_end()
                return [MeasurementInstruction(r_name, r_start, q_name, q_start, q_end)]
            else:
                raise Exception("Unimplemented")
        else:
            raise Exception("Unexpected statement type: " + str(stmt.__dict__))

    def convert_classical_arg(self, arg):
        if arg.type == "uint":
            return UIntArgument(arg.value)
        elif arg.type == "v_ident":
            return CRegArgument(arg.name)
        else:
            raise Exception("Unexpected argument type: '" + arg.type + "'")

    def convert_quantum_arg(self, arg):
        if arg.type == "v_ident":
            return QuantumRegArgument(arg.name)
        elif arg.type == "q_slice":
            start, end = arg.get_start_end()
            return QuantumSliceArgument(arg.get_name().name, start, end)
        elif arg.type == "q_index":
            pos = arg.get_pos()
            return QuantumIndexArgument(arg.get_name().name, pos)


class OpenQASMProgram:
    """
    Stores information for a complete OpenQASM program generated from a certain region.
    """
    def __init__(self, qubits: int, instructions: list, dependencies: set, measurement_qubit_needed: bool):
        self.qubits = qubits
        self.instructions = instructions
        self.dependencies = dependencies
        self.measurement_qubit_needed = measurement_qubit_needed

    def add_instruction(self, instructions):
        self.instructions += instructions

    def emit(self):
        emission = ""
        if self.measurement_qubit_needed:
            emission += "qreg " + MEASUREMENT_QUBIT_NAME + "[1];\n"
        for instruction in self.instructions:
            emission += instruction.emit()
        return emission


class OpenQASMGate:
    def __init__(self, name, cargs, qargs, instructions):
        self.name = name
        self.instructions = instructions
        self.cargs = cargs
        self.qargs = qargs

    def add_instruction(self, instructions):
        self.instructions += instructions

    def emit(self):
        header = "gate " + self.name + " (" + ",".join(self.cargs) + ") " + ",".join(self.qargs) + "{\n  "
        body = "  ".join([instruction.emit() for instruction in self.instructions])
        tail = "}"
        return header + body + tail
