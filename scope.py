from payloads import Payload
from copy import deepcopy
from errors import CompilerError
from builtin_types import Types


class AST:
    def __init__(self):
        self.top_level_scope = Scope(1, 1)
        self.context = self.top_level_scope
        self.functions = {}
        self.regions = {}

    def next(self) -> bool:
        i = self.context.placement()
        if i is not None:
            self.context = self.context.super()
            if self.context.sub_len() > i + 1:
                self.context = self.context.sub_scope(i + 1)
                return True
            else:
                return False
        else:
            return False

    def previous(self) -> bool:
        i = self.context.placement()
        if i is not None:
            self.context = self.context.super()
            if i - 1 >= 0:
                self.context = self.context.sub_scope(i - 1)
                return True
            else:
                return False
        else:
            return False

    def create_sub_scope(self, line, column, payload: Payload = None):
        return self.context.create_sub_scope(line, column, payload=payload)

    def go_to_top(self):
        self.context = self.top_level_scope

    def jump_super(self):
        if self.context.super_scope is not None:
            self.context = self.context.super_scope

    def jump_to(self, ID) -> bool:
        s = self.context.scope_with_id(ID)
        if s is not None:
            self.context = s
            return True
        else:
            return False

    def add_function(self, name, scope):
        if name in self.functions:
            scope.raise_compiler_error("F4", info=name)
        self.functions[name] = scope

    def add_region(self, name, scope):
        if name in self.functions:
            scope.raise_compiler_error("R0", info=name)
        self.regions[name] = scope


class Scope:
    uid = 0

    def __init__(self, line: int, column: int, scope_payload: Payload = None, super_scope=None):
        self.line = line
        self.column = column
        self.var_identifiers = {}
        self.classical_registry = {}
        self.super_scope = super_scope
        self.sub_scopes = []
        if scope_payload is not None:
            scope_payload.set_scope(self)
        self.payload = scope_payload
        self.ID = Scope.uid

        # This is for compatibility with "Visitor" traversal
        self.data = scope_payload.type if scope_payload is not None else ""
        self.children = self.sub_scopes

        # Increment the global ID nonce
        Scope.uid += 1

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def __getattr__(self, item):
        if item[0:4] == "get_" or item in self.payload.__dict__:
            return super().__getattribute__("payload").__getattribute__(item)
        else:
            raise AttributeError("Attribute '" + item + "' not found in Scope object")

    def debug_print(self, indents=0):
        p = self.payload.__dict__ if self.payload is not None else {}
        print(" " * indents + self.data + ":<" + str(self.line) + "," + str(self.column) + ">(" + str(p) + ")")
        for child in self.sub_scopes:
            child.debug_print(indents=indents+1)

    def validate(self):
        if self.payload is not None:
            self.payload.validate()
        else:
            pass

    def create_sub_scope(self, line, column, payload=None):
        s = Scope(line, column, scope_payload=payload, super_scope=self)
        self.sub_scopes.append(s)
        return s

    def register_variable(self, name, v_type):
        # Check that the type is valid
        if not Types.is_valid(v_type.name):
            v_type.raise_compiler_error("T0", info=v_type.name)
        if name.name in self.var_identifiers.keys():
            if Types.is_quantum(v_type.name):
                name.raise_compiler_error("Q2", info=name.name)
            else:
                name.raise_compiler_error("C0", info=name.name)
        else:
            self.var_identifiers[name.name] = v_type

    def get_type_for(self, v_name):
        if v_name in self.var_identifiers:
            return self.var_identifiers[v_name]
        else:
            if self.super_scope is not None:
                t = self.super_scope.get_type_for(v_name)
                return t
            return None

    def set_classical_value(self, name, value):
        if name in self.var_identifiers:
            self.classical_registry[name] = value
            return True
        else:
            if self.super_scope is not None:
                t = self.super_scope.set_classical_value(name, value)
                return t
            return False

    def get_classical_value(self, name):
        if name in self.classical_registry:
            return self.classical_registry[name]
        else:
            if self.super_scope is not None:
                return self.super_scope.get_classical_value(name)
            return None

    def raise_compiler_error(self, error_code, info=""):
        raise CompilerError(error_code, self.line, self.column, info=info)

    def scope_with_id(self, ID):
        if self.ID == ID:
            return self
        for subs in self.sub_scopes:
            s = subs.scope_with_id(ID)
            if s is not None:
                return s
        return None
