from .builtin_types import Types

TYPE_NO_RETURN = "_PLACEHOLDER"

# A Payload is a packet of information stored in an AST node
class Payload:
    def __init__(self, p_type):
        self.type = p_type
        self.owning_scope = None

    def set_scope(self, scope):
        self.owning_scope = scope

    def validate(self) -> bool:
        return True


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

    def get_type(self):
        for t in self.owning_scope.children:
            if t.data == "type":
                return t
        return TypePayload(TYPE_NO_RETURN)

    def get_arg_list(self):
        for a in self.owning_scope.children:
            if a.data == "arg_list":
                return a
        return ArgListPayload()


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
            if c == "call_list":
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


class IfPayload(Payload):
    def __init__(self):
        super().__init__("if")


class QIfPayload(Payload):
    def __init__(self):
        super().__init__("qif")


class FIdentPayload(Payload):
    def __init__(self, name):
        super().__init__("f_ident")
        self.name = name


class VIdentPayload(Payload):
    def __init__(self, name):
        super().__init__("v_ident")
        self.name = name


class RIdentPayload(Payload):
    def __init__(self, name):
        super().__init__("r_ident")
        self.name = name


class TypePayload(Payload):
    def __init__(self, name, quantum=False, measured=False):
        super().__init__("type")
        self.name = name
        self.quantum = quantum
        self.measured = measured


class UIntPayload(Payload):
    def __init__(self, val):
        super().__init__("uint")
        self.value = val


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

    def is_quantum(self):
        return self.get_type().quantum


class RegionPayload(Payload):
    def __init__(self):
        super().__init__("region")

    def get_qubit_cap(self):
        for c in self.owning_scope.children:
            if c.type == "uint":
                return c
        raise Exception("No qubit count for region!")
