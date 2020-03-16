from visitor import Visitor
from errors import CompilerError


class ErrorChecker(Visitor):
    def __init__(self, ast):
        ast.go_to_top()
        super().__init__(ast.context)
        self.errors = []

    def visit_any(self, scope):
        try:
            scope.validate()
        except CompilerError as c:
            self.errors.append(c)

    def errors_occurred(self):
        return len(self.errors) > 0

    def print_errors(self):
        for e in self.errors:
            print(e)


