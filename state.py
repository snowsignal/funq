

class State:
    def __init__(self, ast):
        self.ast = ast
        self.functions = {}
        self.regions = {}

    def register_function(self, scope):
        name: str = scope.get_name().name
        block = scope.get_block()
        classical_args = scope.get_classical_arguments()
        quantum_args = scope.get_quantum_arguments()
        if name in self.functions:
            raise Exception("Function was already declared.")
        else:
            self.functions[name] = (classical_args, quantum_args, block)

    def register_region(self, scope):
        name: str = scope.get_name().name
        qubits: int = scope.get_qubit_cap()
        block = scope.get_block()
        if name in self.regions:
            raise Exception("Region was already declared.")
        else:
            self.regions[name] = (qubits, block)

    def build_from_ast(self):
        # Jump to the top scope
        self.ast.go_to_top()
        # Register functions and regions
        for scope in self.ast.context.sub_scopes:
            if scope.payload.type == "function":
                # Register function
                self.register_function(scope)
            elif scope.payload.type == "region":
                # Register region
                self.register_region(scope)

