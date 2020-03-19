from visitor import Visitor
from errors import CompilerError
from builtin_types import Types


class ErrorChecker(Visitor):
    """
    The ErrorChecker is a Visitor which checks for logic or type errors in the program.
    When calling the traverse() method, exceptions will be raised if the checker finds
    invalid code.
    """
    def __init__(self, ast, state):
        ast.go_to_top()
        super().__init__(ast.context)
        self.ast = ast
        self.state = state
        # region_counter, qubit_max, and current_region are used for checking the qubit allowance for a region.
        # Since an ErrorChecker can only visit one region at a time, there only needs to be
        # one counter, which is for the current region being visited.
        # Each time a new region is visited, the values reset and qubit_max is set to the region's qubit allowance.
        # Whenever a quantum declaration is visited, the region_counter is incremented. If the region_counter passes
        # the qubit_max, an error is thrown. current_region is a variable that is passed to the info field of
        # raise_compiler_error if an error occurs.
        self.region_counter = 0
        self.qubit_max = 0
        self.current_region = ""
        # in_region allows the checker to see if its working in a region or a function
        self.in_region = False
        # current_function keeps track of the current function being visited, if there is one
        self.current_function = ""
        # measured_variables keeps track of what quantum variables have been measured. This is reset after each region.
        self.measured_variables = []

    def verify_arg_types(self, arguments):
        """ Verify that a function's arguments are not register values"""
        for arg in arguments.get_arguments():
            if Types.is_register(arg.get_type().name):
                arg.get_type().raise_compiler_error("F6")

    def verify_one_quantum_arg(self, arguments):
        """ Verify that a function has at least one quantum argument"""
        for arg in arguments.get_arguments():
            if Types.is_quantum(arg.get_type().name):
                return
        arguments.raise_compiler_error("F7", info=self.current_function)

    def visit_region(self, scope):
        self.in_region = True
        self.current_region = scope.get_name().name
        self.region_counter = 1 if self.ast.does_region_need_measurement_qubit(self.current_region) else 0
        self.qubit_max = scope.get_qubit_cap()

    def after_visit_region(self, _):
        self.in_region = False
        self.measured_variables = []

    def visit_q_decl(self, scope):
        if not self.in_region:
            scope.raise_compiler_error("F0")
        t = scope.get_type()
        if not Types.is_quantum(t.name) or not Types.is_register(t.name):
            t.raise_compiler_error("Q0")
        length = scope.get_length()
        self.region_counter += length
        if self.region_counter > self.qubit_max:
            if self.ast.does_region_need_measurement_qubit(self.current_region):
                scope.raise_compiler_error("R1N", info=(scope.get_name().name, self.current_region))
            else:
                scope.raise_compiler_error("R1", info=(scope.get_name().name, self.current_region))

    def visit_c_decl(self, scope):
        if not self.in_region:
            scope.raise_compiler_error("F0")

        t = scope.get_type()
        if Types.is_quantum(t.name):
            t.raise_compiler_error("C4")

        expr = scope.get_expression()
        if expr.data == "c_lit" and not Types.is_register(t.name):
            expr.raise_compiler_error("C5")
        elif Types.is_register(t.name) and not expr.data == "c_lit":
            expr.raise_compiler_error("C5")

    def visit_measurement(self, scope):
        if not self.in_region:
            scope.raise_compiler_error("F0")
        name = scope.get_q_expr().get_name().name
        if name in self.measured_variables:
            scope.raise_compiler_error("Q5")
        else:
            # Check bounds
            start = scope.get_r_start().value
            expr = scope.get_q_expr()
            if expr.data == "q_slice":
                q_start, q_end = expr.get_start_end()
            else:
                q_start = expr.get_pos()
                q_end = q_start
            r_name = scope.get_r_name().name
            c_size = scope.get_scope_for(r_name).super_scope.get_length()
            q_size = scope.get_scope_for(name).super_scope.get_length()
            slice_range = q_end - q_start
            if q_end >= q_size or slice_range + q_start >= q_size:
                if expr.data == "q_slice":
                    scope.raise_compiler_error("Q2", info=(q_start, q_end))
                else:
                    scope.raise_compiler_error("Q3", info=q_start)
            elif q_end >= c_size or slice_range + start >= c_size:
                scope.raise_compiler_error("C3", info=(start, start + slice_range))

    def after_visit_measurement(self, scope):
        self.measured_variables.append(scope.get_q_expr().get_name().name)

    def visit_function(self, scope):
        self.current_function = scope.get_name().name
        self.verify_arg_types(scope.get_arg_list())
        self.verify_one_quantum_arg(scope.get_arg_list())

    def visit_function_call(self, scope):
        name = scope.get_name()
        if not self.in_region:
            # Verify the function being called is not itself, to prevent recursion
            if name.name == self.current_function:
                scope.raise_compiler_error("F1")

        args = self.state.get_arguments_for(name)
        call_args = scope.get_call_list().get_arguments()
        if len(call_args) != len(args):
            scope.raise_compiler_error("F2")
        for (i, c_arg) in enumerate(call_args):
            if args[i][1] != c_arg.get_type_name():
                c_arg.raise_compiler_error("F3", info=(args[i][0], name.name, args[i][1], c_arg.get_type_name()))

    def visit_v_ident(self, scope):
        if scope.name in self.measured_variables:
            scope.raise_compiler_error("Q6")

    def after_visit_function(self, _):
        self.current_function = ""
