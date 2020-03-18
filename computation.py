from visitor import Transformer
from builtin_types import Types
from payloads import UIntPayload
from scope import Scope
import operator


class ComputationHandler(Transformer):
    """
    The ComputationHandler transforms the AST by registering declarations of constant variables, and then
    replacing identifiers for constant variables in the tree with the declared constant values. Finally, it evaluates
    expressions that add, subtract, multiply, and divide constant numbers, replacing those expressions in the tree with
    a single numeric value.
    """
    def __init__(self, ast):
        ast.go_to_top()
        super().__init__(ast.context)

        self.in_region = False

    def transform_region(self, scope):
        self.in_region = True
        return scope

    def transform_function(self, scope):
        self.in_region = False
        return scope

    def is_const(self, scope):
        typename = scope.get_type_for(scope.name).name
        return Types.is_classical(typename) and not Types.is_register(typename)

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
        if not self.in_region:
            return scope
        if scope.get_type().name == "Const":
            expr = scope.get_expression()
            scope.set_classical_value(scope.get_name().name, self.evaluate_expression(expr))
            return None
        else:
            return scope

    def transform_v_ident(self, scope):
        if not self.in_region:
            return scope
        if self.is_const(scope):
            value = scope.get_classical_value(scope.name)
            s = Scope(scope.line, scope.column, scope_payload=UIntPayload(value), super_scope=scope.super_scope)
            return s
        else:
            return scope

    def transform_operation(self, scope):
        if not self.in_region:
            return scope
        value = self.evaluate_expression(scope)
        s = Scope(scope.line, scope.column, scope_payload=UIntPayload(value), super_scope=scope.super_scope)
        return s
