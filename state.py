from standard_library import StandardLibrary


class State:
    def __init__(self, ast):
        self.ast = ast
        self.functions = {}
        self.regions = {}
        for name in ast.regions.keys():
            region = ast.regions[name][0]
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

    def find_dependencies(self, scope) -> set:
        dependencies = set()
        for stmt in scope.children:
            if stmt.data == "function_call":
                name = stmt.get_name().name
                if not StandardLibrary.is_standard(name):
                    dependencies.add(name)
            elif stmt.data == "if":
                dependencies = dependencies.union(
                    self.find_dependencies(stmt.get_block())
                )
        return dependencies

    def register_region(self, name, scope):
        qubits: int = scope.get_qubit_cap()
        block = scope.get_block()
        dependencies = self.find_dependencies(block)
        if name in self.regions:
            raise Exception("Region was already declared.")
        else:
            self.regions[name] = (
                qubits,
                block,
                self.ast.does_region_need_measurement_qubit(name),
                dependencies,
            )

    def get_arguments_for(self, function_name):
        if function_name.name in self.functions.keys():
            scope = self.functions[function_name.name][2].super_scope
            args = scope.get_arg_list()
            str_args = []
            for arg in args.get_arguments():
                name = arg.get_name().name
                type = arg.get_type().name
                str_args.append((name, type))
            return str_args
        elif StandardLibrary.is_standard(function_name.name):
            return StandardLibrary.get_standard_args(function_name.name)
        else:
            function_name.raise_compiler_error("F8", info=function_name.name)
