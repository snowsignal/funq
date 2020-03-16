from errors import CompilerError
from visitor import Visitor

# The Resolver transforms expressions and resolves types of identifiers
class Resolver(Visitor):
    def __init__(self, ast):
        ast.go_to_top()
        super().__init__(ast.context)

    def visit_function(self, scope):
        name = scope.get_name()
        args = scope.get_arg_list()
        for arg in args.get_arguments():
            a_name = arg.get_name().name
            type = arg.get_type().name
            scope.var_identifiers.append((a_name, type))
        scope.super_scope.function_identifiers.append(name)
