from output import Output

class State:
    def __init__(self, ast):
        self.ast = ast
        self.classes = []
        self.functions = []

    def build_from_ast(self):
        output = ""
        # Jump to the top scope
        self.ast.go_to_top()
        # Register functions and regions
        for scope in self.ast.context.sub_scopes:
            if scope.payload.type == "function":
                # Register function
                self.register_function(scope)
            elif scope.payload.type == "class":
                # Register region
                self.register_class(scope.payload)
