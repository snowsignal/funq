

class State:
    def __init__(self, ast):
        self.ast = ast
        self.functions = {}
        self.regions = {}

    def register_function(self, scope):
        name: str = scope.children[0].payload.name
        return_name: int = scope.children[1].payload.name
        is_measured: bool = scope.children[1].payload.measured
        block = scope.children[2]
        if name in self.functions:
            raise Exception("Function was already declared.")
        else:
            self.functions[name] = ((return_name, is_measured), block)

    def register_region(self, scope):
        name: str = scope.children[0].payload.name
        qubits: int = scope.children[1].payload.value
        block = scope.children[2]
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

