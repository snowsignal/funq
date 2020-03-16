from visitor import Visitor
from lark import Token, Tree
from payloads import *
from copy import deepcopy
from math import ceil
from errors import CompilerError


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

    def create_sub_scope(self, line, column, payload=None):
        return self.context.create_sub_scope(line, column, payload=payload)

    def go_to_top(self):
        self.context = self.top_level_scope

    def jump_super(self):
        if self.context.super_scope is not None:
            self.context = self.context.super_scope

    def jump_to(self, id) -> bool:
        s = self.context._scope_with_id(id)
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

    def __init__(self, line, column, scope_payload=None, super_scope=None):
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

    def print(self, indents=0):
        p = self.payload.__dict__ if self.payload is not None else {}
        print(" " * indents + self.data + ":<" + str(self.line) + "," + str(self.column) + ">(" + str(p) + ")")
        for child in self.sub_scopes:
            child.print(indents=indents+1)

    def validate(self):
        if self.payload is not None:
            self.payload.validate()
        else:
            pass

    def scope_print(self, indents=0):
        print(" " * indents + self.data + ":" + str(self.var_identifiers) + str(self.classical_registry))
        for child in self.sub_scopes:
            child.scope_print(indents=indents+1)

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

    def _scope_with_id(self, ID):
        if self.ID == ID:
            return self
        for subs in self.sub_scopes:
            s = subs._scope_with_id(ID)
            if s is not None:
                return s
        return None


def token_to_str(t: Token) -> str:
    return t.value


def get_line_column(t: Tree) -> (int, int):
    return ceil(t.meta.line / 2), t.meta.column


class ASTBuilder(Visitor):
    def __init__(self, syntax_tree):
        super().__init__(syntax_tree)
        self.ast = AST()

    def visit_function_def(self, t):
        line, column = get_line_column(t)
        scope = self.ast.create_sub_scope(line, column, payload=FunctionPayload())
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_function_def(self, _):
        self.ast.jump_super()

    def visit_region(self, t):
        line, column = get_line_column(t)
        scope = self.ast.create_sub_scope(line, column, payload=RegionPayload())
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_region(self, _):
        self.ast.jump_super()

    def visit_function_call(self, t):
        line, column = get_line_column(t)
        scope = self.ast.create_sub_scope(line, column, payload=FunctionCallPayload())
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_function_call(self, _):
        self.ast.jump_super()

    def visit_if(self, t):
        line, column = get_line_column(t)
        scope = self.ast.create_sub_scope(line, column, payload=IfPayload())
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_if(self, _):
        self.ast.jump_super()

    def visit_sum(self, t):
        expr = t.children[0]
        print(expr.data)
        if expr.data == "product":
            return
        elif expr.data in ["add", "sub"]:
            line, column = get_line_column(t)
            scope = self.ast.create_sub_scope(line, column, payload=OpPayload(expr.data))
            if not self.ast.jump_to(scope.ID):
                raise Exception("could not jump to scope")
        else:
            raise Exception("Invalid expression data")

    def visit_product(self, t):
        expr = t.children[0]
        print(expr.data)
        if expr.data == "atomic":
            return
        elif expr.data in ["mul", "div"]:
            line, column = get_line_column(t)
            scope = self.ast.create_sub_scope(line, column, payload=OpPayload(expr.data))
            if not self.ast.jump_to(scope.ID):
                raise Exception("could not jump to scope")
        else:
            raise Exception("Invalid expression data")

    def after_visit_sum(self, t):
        expr = t.children[0]
        if expr.data == "product":
            return
        self.ast.jump_super()

    def after_visit_product(self, t):
        expr = t.children[0]
        if expr.data == "atomic":
            return
        self.ast.jump_super()

    def visit_b_expr(self, t):
        op = t.children[0]
        if op.data in ["eq", "neq", "greater", "lesser"]:
            line, column = get_line_column(t)
            scope = self.ast.create_sub_scope(line, column, payload=BoolOpPayload(op.data))
            if not self.ast.jump_to(scope.ID):
                raise Exception("could not jump to scope")
        else:
            raise Exception("Invalid boolean expression data")

    def after_visit_b_expr(self, _):
        self.ast.jump_super()

    def visit_block(self, t):
        line, column = get_line_column(t)
        scope = self.ast.create_sub_scope(line, column, payload=BlockPayload())
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_block(self, _):
        self.ast.jump_super()

    def visit_assignment(self, t):
        line, column = get_line_column(t)
        scope = self.ast.create_sub_scope(line, column, payload=AssignmentPayload())
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_assignment(self, _):
        self.ast.jump_super()

    def visit_type(self, t):
        line, column = get_line_column(t)
        name = token_to_str(t.children[0])
        self.ast.create_sub_scope(line, column, payload=TypePayload(name))

    def visit_f_ident(self, t):
        line, column = get_line_column(t)
        name = token_to_str(t.children[0])
        self.ast.create_sub_scope(line, column, payload=FIdentPayload(name))

    def visit_v_ident(self, t):
        line, column = get_line_column(t)
        name = token_to_str(t.children[0])
        self.ast.create_sub_scope(line, column, payload=VIdentPayload(name))

    def visit_r_ident(self, t):
        line, column = get_line_column(t)
        name = token_to_str(t.children[0])
        self.ast.create_sub_scope(line, column, payload=RIdentPayload(name))

    def visit_uint(self, t):
        line, column = get_line_column(t)
        # This will always succeed since only ints are parsed in the first place.
        val = int(token_to_str(t.children[0]))
        self.ast.create_sub_scope(line, column, payload=UIntPayload(val))

    def visit_call_list(self, t):
        if self.ast.context.super_scope.data == "call_list":
            self.ast.jump_super()
            return
        if self.ast.context.data == "call_list":
            return
        line, column = get_line_column(t)
        scope = self.ast.create_sub_scope(line, column, payload=CallListPayload())
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_call_list(self, _):
        if self.ast.context.data == "call_list" and not self.ast.context.super_scope.data == "call_list":
            self.ast.jump_super()

    def visit_arg(self, t):
        line, column = get_line_column(t)
        scope = self.ast.create_sub_scope(line, column, payload=ArgPayload())
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_arg(self, _):
        self.ast.jump_super()

    def visit_arg_list(self, t):
        if self.ast.context.super_scope.data == "arg_list" or self.ast.context.data == "arg_list":
            return
        line, column = get_line_column(t)
        scope = self.ast.create_sub_scope(line, column, payload=ArgListPayload())
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_arg_list(self, _):
        if self.ast.context.data == "arg_list":
            self.ast.jump_super()

    def visit_q_slice(self, t):
        line, column = get_line_column(t)
        scope = self.ast.create_sub_scope(line, column, payload=QuantumSlicePayload())
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_q_slice(self, _):
        self.ast.jump_super()

    def visit_q_lit(self, t):
        line, column = get_line_column(t)
        scope = self.ast.create_sub_scope(line, column, payload=QuantumLiteralPayload())
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def visit_qubit(self, t):
        line, column = get_line_column(t)
        v = t.children[0].value
        value = v == "1"
        scope = self.ast.create_sub_scope(line, column, payload=QubitPayload(value))
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_q_lit(self, _):
        self.ast.jump_super()

    def after_visit_qubit(self, _):
        self.ast.jump_super()

    def visit_q_declaration(self, t):
        line, column = get_line_column(t)
        scope = self.ast.create_sub_scope(line, column, payload=QuantumDeclarationPayload())
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_q_declaration(self, _):
        self.ast.jump_super()

    def visit_q_index(self, t):
        line, column = get_line_column(t)
        scope = self.ast.create_sub_scope(line, column, payload=QuantumIndexPayload())
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_q_index(self, _):
        self.ast.jump_super()

    def visit_declaration(self, t):
        line, column = get_line_column(t)
        scope = self.ast.create_sub_scope(line, column, payload=ClassicalDeclarationPayload())
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_declaration(self, _):
        self.ast.jump_super()

    def visit_measurement(self, t):
        line, column = get_line_column(t)
        scope = self.ast.create_sub_scope(line, column, payload=MeasurementPayload())
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_measurement(self, _):
        self.ast.jump_super()
