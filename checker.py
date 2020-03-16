from visitor import Visitor
from errors import CompilerError


class ErrorChecker(Visitor):
    def __init__(self, ast):
        ast.go_to_top()
        super().__init__(ast.context)
        self.errors = []
        self.region_counter = 0
        self.qubit_max = 0
        self.current_region = ""

    def visit_region(self, scope):
        self.current_region = scope.get_name().name
        self.region_counter = 0
        self.qubit_max = scope.get_qubit_cap().value

    def visit_q_decl(self, scope):
        length = scope.get_length()
        self.region_counter += length
        if self.region_counter > self.qubit_max:
            scope.raise_compiler_error("Q1", info=scope.get_name().name)

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


