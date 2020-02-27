class State:
    def __init__(self):
        self.top_level_scope = Scope()


class Scope:
    def __init__(self, functions=None, identifiers=None, super_scope=None):
        if identifiers is None:
            self.identifiers = []
        if functions is None:
            self.functions = []
        self.super_scope = super_scope
        self.sub_scopes = []

    def has_identifier(self, identifier_name):
        for i in self.identifiers:
            if i.name == identifier_name:
                return True
        if self.super_scope is not None:
            return self.super_scope.has_identifier(identifier_name)
        else:
            return False

    def add_function(self, function):
        self.functions.append(function)

    def add_identifier(self, identifier):
        self.identifiers.append(identifier)

    def create_sub_scope(self, functions=None, identifiers=None):
        scope = Scope(functions=functions, identifiers=identifiers, super_scope=self)
        self.sub_scopes.append(scope)
        return scope
