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


class FunctionCallPayload(Payload):
    def __init__(self):
        super().__init__("function_call")


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


class CallListPayload(Payload):
    def __init__(self):
        super().__init__("call_list")
