from standard_library import StandardLibrary

class State:
    def __init__(self, ast):
        self.functions = {}
        self.regions = {}
        for name in ast.regions.keys():
            region = ast.regions[name]
            self.register_region(name, region)
        for name in ast.functions.keys():
            function = ast.functions[name]
            self.register_function(name, function)

    def register_function(self, name, scope):
        block = scope.get_block()
        classical_args = scope.get_classical_arguments()
        quantum_args = scope.get_quantum_arguments()
        if name in self.functions:
            raise Exception("Function was already declared.")
        else:
            self.functions[name] = (classical_args, quantum_args, block)

    def register_region(self, name, scope):
        qubits: int = scope.get_qubit_cap()
        block = scope.get_block()
        if name in self.regions:
            raise Exception("Region was already declared.")
        else:
            self.regions[name] = (qubits, block)

    def get_arguments_for(self, function_name):
        if function_name in self.functions.keys():
            scope = self.functions[function_name]
            args = scope.get_arg_list()
            str_args = []
            for arg in args.get_arguments():
                name = arg.get_name().name
                type = arg.get_type().name
                str_args.append((name, type))
            return str_args
        elif StandardLibrary.is_standard(function_name):
            return StandardLibrary.get_standard_args(function_name)
