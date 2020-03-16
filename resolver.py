from errors import CompilerError
from visitor import Visitor

# The Resolver transforms expressions and resolves types of identifiers
class Resolver(Visitor):
    def __init__(self, ast):
        self.ast = ast
        self.ast.go_to_top()
        super().__init__(self.ast.context)

    def visit_function(self, scope):
        name = scope.get_name()
        args = scope.get_arg_list()
        for arg in args.get_arguments():
            a_name = arg.get_name()
            type = arg.get_type()
            scope.register_variable(a_name, type)
        self.ast.add_function(name, scope)

    def visit_region(self, scope):
        name = scope.get_name()
        self.ast.add_region(name, scope)

    def visit_c_decl(self, scope):
        name = scope.get_name()
        v_type = scope.get_type()
        scope.super_scope.register_variable(name, v_type)

    def visit_q_decl(self, scope):
        name = scope.get_name()
        v_type = scope.get_type()
        scope.super_scope.register_variable(name, v_type)

    def visit_v_ident(self, scope):
        v_type = scope.get_type_for(scope.name)
        if v_type is None:
            scope.raise_compiler_error("V0", info=scope.name)
        else:
            scope.payload.resolve_type(v_type.name)
