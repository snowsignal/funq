from builtin_types import Types
from errors import CompilerError

TYPE_NO_RETURN = "_NO_RETURN"


# A Payload is a packet of information stored in an AST node
class Payload:
    def __init__(self, p_type):
        self.type = p_type
        self.owning_scope = None

    def set_scope(self, scope):
        self.owning_scope = scope

    def validate(self):
        return


class FunctionPayload(Payload):
    def __init__(self):
        super().__init__("function")

    def get_name(self):
        for n in self.owning_scope.children:
            if n.data == "f_ident":
                return n
        raise Exception("No name for function!")

    def get_block(self):
        for b in self.owning_scope.children:
            if b.data == "block":
                return b
        raise Exception("No block in function!")

    def get_classical_arguments(self) -> list:
        arguments = self.owning_scope.get_arg_list().get_arguments()
        classical_args = []
        for arg in arguments:
            if Types.is_classical(arg.get_type().name):
                classical_args.append(arg)
        return classical_args

    def get_quantum_arguments(self) -> list:
        arguments = self.owning_scope.get_arg_list().get_arguments()
        quantum_args = []
        for arg in arguments:
            if Types.is_quantum(arg.get_type().name):
                quantum_args.append(arg)
        return quantum_args

    def get_arg_list(self):
        for a in self.owning_scope.children:
            if a.data == "arg_list":
                return a
        return ArgListPayload()

    def validate(self):
        pass


class FunctionCallPayload(Payload):
    def __init__(self):
        super().__init__("function_call")

    def get_name(self):
        for n in self.owning_scope.children:
            if n.data == "f_ident":
                return n
        raise Exception("No name for function call!")

    def get_call_list(self):
        for c in self.owning_scope.children:
            if c.data == "call_list":
                return c
        raise Exception("No call list for function call!")


class AssignmentPayload(Payload):
    def __init__(self):
        super().__init__("assignment")


class BlockPayload(Payload):
    def __init__(self):
        super().__init__("block")


class OpPayload(Payload):
    def __init__(self, op):
        super().__init__("operation")
        self.operation = op

    def get_operation(self):
        op = self.operation
        if op == "add":
            return "+"
        elif op == "sub":
            return "-"
        elif op == "mul":
            return "*"
        elif op == "div":
            return "/"


class BoolOpPayload(Payload):
    def __init__(self, op):
        super().__init__("b_expr")
        self.operation = op

    def get_operation(self):
        op = self.operation
        if op == "eq":
            return "=="
        elif op == "neq":
            return "!="
        elif op == "greater":
            return ">"
        elif op == "lesser":
            return "<"


class IfPayload(Payload):
    def __init__(self):
        super().__init__("if")

    def get_args(self):
        comp = self.owning_scope.children[0].children
        return comp[0], comp[2]

    def get_op(self):
        comp = self.owning_scope.children[0]
        if comp.data == "eq":
            return "=="
        elif comp.data == "neq":
            return "!="
        elif comp.data == "greater":
            return ">"
        elif comp.data == "lesser":
            return "<"


class FIdentPayload(Payload):
    def __init__(self, name):
        super().__init__("f_ident")
        self.name = name


class VIdentPayload(Payload):
    def __init__(self, name, type=""):
        super().__init__("v_ident")
        self.name = name
        self.v_type = type

    def resolve_type(self, type):
        self.v_type = type

    def get_type_name(self):
        return self.v_type


class RIdentPayload(Payload):
    def __init__(self, name):
        super().__init__("r_ident")
        self.name = name


class TypePayload(Payload):
    def __init__(self, name):
        super().__init__("type")
        self.name = name


class UIntPayload(Payload):
    def __init__(self, val):
        super().__init__("uint")
        self.value = val

    def get_type(self):
        return "Const"


class CallListPayload(Payload):
    def __init__(self):
        super().__init__("call_list")

    def get_classical_arguments(self) -> list:
        arguments = self.owning_scope.children
        classical_args = []
        for arg in arguments:
            if Types.is_classical(arg.get_type()):
                classical_args.append(arg)
        return classical_args

    def get_quantum_arguments(self) -> list:
        arguments = self.owning_scope.children
        quantum_args = []
        for arg in arguments:
            if Types.is_quantum(arg.get_type()):
                quantum_args.append(arg)
        return quantum_args


class ArgListPayload(Payload):
    def __init__(self):
        super().__init__("arg_list")

    def get_arguments(self):
        return self.owning_scope.children


class ArgPayload(Payload):
    def __init__(self):
        super().__init__("arg")

    def get_name(self):
        return self.owning_scope.children[0]

    def get_type(self):
        return self.owning_scope.children[1]


class RegionPayload(Payload):
    def __init__(self):
        super().__init__("region")

    def get_name(self):
        for n in self.owning_scope.children:
            if n.type == "r_ident":
                return n
        raise Exception("No name for region!")

    def get_qubit_cap(self):
        for c in self.owning_scope.children:
            if c.type == "uint":
                return c
        raise Exception("No qubit count for region!")

    def get_block(self):
        for b in self.owning_scope.children:
            if b.type == "block":
                return b
        raise Exception("No block for region!")


class QuantumSlicePayload(Payload):
    def __init__(self):
        super().__init__("q_slice")

    def get_start_end(self):
        return self.owning_scope.children[0].value, self.owning_scope.children[1].value

    def get_type_name(self):
        return "Q"


class QuantumLiteralPayload(Payload):
    def __init__(self):
        super().__init__("q_lit")

    def get_qubit_length(self):
        return len(self.owning_scope.children)


class ClassicalDeclarationPayload(Payload):
    def __init__(self):
        super().__init__("c_decl")

    def get_type(self):
        return self.owning_scope.children[0]

    def get_name(self):
        return self.owning_scope.children[1]

    def get_expression(self):
        return self.owning_scope.children[2]


class QuantumDeclarationPayload(Payload):
    def __init__(self):
        super().__init__("q_decl")

    def get_type(self):
        return self.owning_scope.children[0]

    def get_name(self):
        return self.owning_scope.children[1]

    def get_length(self):
        return self.owning_scope.children[2].get_qubit_length()


class QubitPayload(Payload):
    def __init__(self, value: bool):
        super().__init__("qubit")
        self.value = value


class QuantumIndexPayload(Payload):
    def __init__(self):
        super().__init__("q_index")


class MeasurementPayload(Payload):
    def __init__(self):
        super().__init__("measurement")
