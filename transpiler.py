from visitor import Visitor
# A Transpiler converts an AST into OpenQASM programs by visiting the nodes
# and converting.
class Transpiler(Visitor):
    def __init__(self, ast):
        ast.go_to_top()
        super().__init__(ast.context)
        self.programs = []

    def visit_if(self, t):
        # An if statement becomes a CNOT gate. First, get all sub-statements:
        statements = t.children[2].children[0].children
        print(statements)


class OpenQASMAST:
    def __init__(self):
        pass
