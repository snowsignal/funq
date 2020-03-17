from visitor import Visitor
from errors import CompilerError


class ErrorChecker(Visitor):
    """
    The ErrorChecker is a Visitor which checks for logic or type errors in the program.
    When calling the traverse() method, exceptions will not be raised directly, but they will
    be stored internally. errors_occured() can be used to check if errors arose during checking,
    and print_errors() will print them to the console in order of occurrence.
    """
    def __init__(self, ast):
        ast.go_to_top()
        super().__init__(ast.context)
        self.errors = []
        # region_counter, qubit_max, and current_region are used for checking the qubit allowance for a region.
        # Since an ErrorChecker can only visit one region at a time, there only needs to be
        # one counter, which is for the current region being visited.
        # Each time a new region is visited, the values reset and qubit_max is set to the region's qubit allowance.
        # Whenever a quantum declaration is visited, the region_counter is incremented. If the region_counter passes
        # the qubit_max, an error is thrown. current_region is a variable used for internal debugging.
        self.region_counter = 0
        self.qubit_max = 0
        self.current_region = ""

    def visit_region(self, scope):
        self.current_region = scope.get_name().name
        self.region_counter = 0
        self.qubit_max = scope.get_qubit_cap()

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


