
class Instruction:
    def __init__(self, instruction_type):
        self.instruction_type = instruction_type

    def emit(self) -> str:
        return "// Empty instruction. You should not be seeing this."


class Hadamard(Instruction):
    def __init__(self, arguments):
        super().__init__("gate_call")
        self.arguments = arguments

    def emit(self) -> str:
        return "h " + self.arguments


class Universal(Instruction):
    pass


class CNot(Instruction):
    pass


class If(Instruction):
    pass


class CReg(Instruction):
    pass


class QReg(Instruction):
    pass


class X(Instruction):
    pass


class Y(Instruction):
    pass


class Z(Instruction):
    pass


class S(Instruction):
    pass


class T(Instruction):
    pass
