from scope import MEASUREMENT_QUBIT_NAME

class InstructionArgument:
    def __init__(self, arg_type):
        self.arg_type = arg_type

    def emit(self) -> str:
        raise Exception("A subclass of InstructionArgument did not override emit")


class UIntArgument(InstructionArgument):
    def __init__(self, value):
        super().__init__("uint")
        self.value = value

    def emit(self) -> str:
        return str(self.value)


class CRegArgument(InstructionArgument):
    def __init__(self, name):
        super().__init__("c_reg")
        self.name = name

    def emit(self) -> str:
        return self.name


class QuantumIndexArgument(InstructionArgument):
    def __init__(self, name, index):
        super().__init__("q_index")
        self.name = name
        self.index = index

    def emit(self) -> str:
        return self.name + "[" + str(self.index) + "]"


class QuantumRegArgument(InstructionArgument):
    def __init__(self, name):
        super().__init__("q_reg")
        self.name = name

    def emit(self) -> str:
        return self.name


class QuantumSliceArgument(InstructionArgument):
    def __init__(self, name, start, end):
        super().__init__("q_slice")
        self.name = name
        self.start = start
        self.end = end
        self.iter = self.start

    def emit(self) -> str:
        return self.name + "[" + str(self.iter) + "]"

    def reset(self):
        self.iter = self.start

    def increment(self) -> bool:
        if self.iter < self.end:
            self.iter += 1
            return True
        else:
            return False


class Instruction:
    def __init__(self, instruction_type):
        self.instruction_type = instruction_type

    def emit(self) -> str:
        return "// Empty instruction. You should not be seeing this."


class FunctionCall(Instruction):
    def __init__(self, name, cargs, qargs):
        super().__init__("func_call")
        self.name = name
        self.cargs = cargs
        self.qargs = qargs

    def emit(self) -> str:
        output = ""
        func = self.name
        if len(self.cargs) == 0:
            header = func + " "
        else:
            header = func + "(" + ','.join([c.emit() for c in self.cargs]) + ") "
        should_repeat = False
        var_to_repeat = None
        for q in self.qargs:
            if q.arg_type == "q_slice":
                should_repeat = True
                var_to_repeat = q
        if should_repeat:
            var_to_repeat.reset()
            while True:
                output += header + ", ".join([q.emit() for q in self.qargs]) + ";\n"
                if not var_to_repeat.increment():
                    break
        else:
            output += header + ", ".join([q.emit() for q in self.qargs]) + ";\n"

        return output


class Comparison:
    def __init__(self, arg1, arg2, op):
        self.arg1 = arg1
        self.arg2 = arg2
        self.op = op

    def perform_operation(self) -> bool:
        if self.op == "==":
            return self.arg1.value == self.arg2.value
        elif self.op == "!=":
            return self.arg1.value != self.arg2.value
        elif self.op == ">":
            return self.arg1.value > self.arg2.value
        elif self.op == "<":
            return self.arg1.value < self.arg2.value
        raise Exception("Invalid operation for Comparison!")

    def compile_time_result(self) -> (bool, bool):
        if self.arg1.arg_type == "uint" and self.arg2.arg_type == "uint":
            return True, self.perform_operation()
        else:
            return False, None

    def emit(self) -> str:
        return self.arg1.emit() + self.op + self.arg2.emit()


class IfInstruction(Instruction):
    def __init__(self, comparison, sub_instructions):
        super().__init__("if")
        self.comparison = comparison
        self.sub_instructions = sub_instructions

    def emit_sub_instructions(self):
        emission = ""
        for i in self.sub_instructions:
            emission += i.emit()
        return emission

    def emit(self) -> str:
        can_resolve, result = self.comparison.compile_time_result()
        if can_resolve:
            if result:
                return self.emit_sub_instructions()
            else:
                return ""
        else:
            instructions = self.emit_sub_instructions().split("\n")
            for i in range(0, len(instructions)-1):
                instructions[i] = "if (" + self.comparison.emit() + ") " + instructions[i]
            return "\n".join(instructions)


class QuantumInitialization(Instruction):
    def __init__(self, name, size, bits):
        super().__init__("q_init")
        self.name = name
        self.size = size
        self.bits = bits

    def emit(self) -> str:
        return "qreg " + self.name + "[" + str(self.size) + "];\n"


class ClassicalInitialization(Instruction):
    def __init__(self, name, size, bits):
        super().__init__("c_init")
        self.name = name
        self.size = size
        self.bits = bits

    def measure_one(self, i):
        return "x " + MEASUREMENT_QUBIT_NAME + "[0];\nmeasure " + MEASUREMENT_QUBIT_NAME + \
               "[0] -> " + self.name + "[" + str(i) + "];\nreset " + MEASUREMENT_QUBIT_NAME + ";\n"

    def emit(self) -> str:
        emission = "creg " + self.name + "[" + str(self.size) + "];\n"
        for i, bit in enumerate(self.bits):
            if bit == "1":
                emission += self.measure_one(i)
        return emission


class MeasurementInstruction(Instruction):
    def __init__(self, r_name, start, q_name, q_start, q_end):
        super().__init__("measurement")
        self.r_name = r_name
        self.start = start
        self.q_name = q_name
        self.q_start = q_start
        self.q_end = q_end

    def emit(self) -> str:
        emission = ""
        length = self.q_end - self.q_start + 1
        for i in range(0, length):
            emission += "measure " + self.q_name + "[" + str(self.q_start + i) + "] -> " + self.r_name + "[" + str(self.start + i) + "];\n"
        return emission
