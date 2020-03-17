from visitor import Transformer
from builtin_types import Types
from payloads import UIntPayload
from scope import Scope
import operator


class ComputationHandler(Transformer):
    def __init__(self, ast):
        ast.go_to_top()
        super().__init__(ast.context)

    def is_classical(self, scope):
        print("Finding type!" + scope.get_type_for(scope.name).name)
        return Types.is_classical(scope.get_type_for(scope.name).name)

    def evaluate_expression(self, scope):
        if scope.data == "uint":
            return scope.value
        elif scope.data == "v_ident":
            return scope.get_classical_value(scope.name)
        elif scope.data == "operation":
            op = scope.get_operation()
            arg1, arg2 = scope.get_operands()
            operation = {
                "+": operator.add,
                "-": operator.sub,
                "*": operator.mul,
                "/": operator.floordiv
            }[op]
            return operation(self.evaluate_expression(arg1), self.evaluate_expression(arg2))

    def transform_c_decl(self, scope):
        if scope.get_type().name == "Const":
            expr = scope.get_expression()
            scope.set_classical_value(scope.get_name().name, self.evaluate_expression(expr))
            return None
        else:
            return scope

    def transform_v_ident(self, scope):
        if self.is_classical(scope):
            value = scope.get_classical_value(scope.name)
            s = Scope(scope.line, scope.column, scope_payload=UIntPayload(value), super_scope=scope.super_scope)
            print(s)
            return s
        else:
            print("Dang it! \"" + scope.name + "\" is not classical!")
            return scope

    def transform_operation(self, scope):
        value = self.evaluate_expression(scope)
        s = Scope(scope.line, scope.column, scope_payload=UIntPayload(value), super_scope=scope.super_scope)
        return s
