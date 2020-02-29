from visitor import Visitor
from payloads import *

class AST:
    def __init__(self):
        self.top_level_scope = Scope()
        self.context = self.top_level_scope
        self.functions = []
        self.classes = []

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

    def create_sub_scope(self, payload=None):
        return self.context.create_sub_scope(payload=payload)

    def go_to_top(self):
        self.context = self.top_level_scope

    def jump_super(self):
        print("Jumping from " + self.context.data)
        if self.context.super_scope is not None:
            self.context = self.context.super_scope

    def jump_to(self, id) -> bool:
        s = self.context._scope_with_id(id)
        print("Entering " + s.data)
        if s is not None:
            self.context = s
            return True
        else:
            return False

    # Perform a final set of validation checks on the generated scopes
    def validate(self):
        pass


class Scope:
    uid = 0

    def __init__(self, scope_payload=None, identifiers=None, super_scope=None):
        if identifiers is None:
            self.identifiers = []
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

    def print(self, indents=0):
        p = self.payload.__dict__ if self.payload is not None else {}
        print(" " * indents + "(" + self.data + ":" + str(p) + ")")
        for child in self.sub_scopes:
            child.print(indents=indents+1)

    def create_sub_scope(self, payload=None):
        s = Scope(scope_payload=payload, super_scope=self)
        self.sub_scopes.append(s)
        return s

    def _scope_with_id(self, ID):
        if self.ID == ID:
            return self
        for subs in self.sub_scopes:
            s = subs._scope_with_id(ID)
            if s is not None:
                return s
        return None

    def verify_type(self, typename):
        return True


class ASTBuilder(Visitor):
    def __init__(self, syntax_tree):
        super().__init__(syntax_tree)
        self.ast = AST()

    def visit_function_def(self, t):
        scope = self.ast.create_sub_scope(payload=FunctionPayload())
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_function_def(self, _):
        self.ast.jump_super()

    def visit_function_call(self, t):
        scope = self.ast.create_sub_scope(payload=FunctionCallPayload())
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_function_call(self, _):
        self.ast.jump_super()

    def visit_if(self, t):
        scope = self.ast.create_sub_scope(payload=IfPayload())
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_if(self, _):
        self.ast.jump_super()

    def visit_qif(self, t):
        scope = self.ast.create_sub_scope(payload=QIfPayload())
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_qif(self, _):
        self.ast.jump_super()

    def visit_expr(self, t):
        expr = t.children[0]
        print("Visiting:", t)
        # There are many kinds of expressions. Check which one it is:
        if expr.data == "paren" \
            or expr.data == "v_ident" \
            or expr.data == "string" \
            or expr.data == "uint":
            return  # These will be processed by their own function
        elif expr.data in ["mul", "div", "add", "sub"]:
            scope = self.ast.create_sub_scope(payload=OpPayload(expr.data))
        else:
            # We shouldn't reach this point. This is if expr.data does not match any
            # of the current expression types.
            raise Exception("INTERNAL ERROR")
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_expr(self, t):
        expr = t.children[0]
        if expr.data == "paren" \
                or expr.data == "v_ident" \
                or expr.data == "string" \
                or expr.data == "uint":
            return
        print("Leaving expr")
        self.ast.jump_super()

    def visit_block(self, t):
        scope = self.ast.create_sub_scope(payload=BlockPayload())
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_block(self, _):
        self.ast.jump_super()

    def visit_assignment(self, t):
        scope = self.ast.create_sub_scope(payload=AssignmentPayload())
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_assignment(self, _):
        self.ast.jump_super()

    def visit_type(self, t):
        name = t.children[0]
        quantum = name == "Q"
        measured = len(t.children) > 1  # Because the second token will always be the '?'
        self.ast.create_sub_scope(payload=TypePayload(name, quantum, measured))

    def visit_f_ident(self, t):
        name = t.children[0]
        self.ast.create_sub_scope(payload=FIdentPayload(name))

    def visit_v_ident(self, t):
        name = t.children[0]
        self.ast.create_sub_scope(payload=VIdentPayload(name))

    def visit_r_ident(self, t):
        name = t.children[0]
        self.ast.create_sub_scope(payload=RIdentPayload(name))

    def visit_uint(self, t):
        val = t.children[0]
        self.ast.create_sub_scope(payload=UIntPayload(val))

    def visit_call_list(self, t):
        print("Visiting:", t)
        if self.ast.context.super_scope.data == "call_list" or self.ast.context.data == "call_list":
            return
        scope = self.ast.create_sub_scope(payload=CallListPayload())
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_call_list(self, _):
        if self.ast.context.data == "call_list":
            self.ast.jump_super()

    def visit_arg(self, t):
        scope = self.ast.create_sub_scope(payload=ArgPayload())
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_arg(self, _):
        self.ast.jump_super()

    def visit_arg_list(self, t):
        print("Visiting:", t)
        if self.ast.context.super_scope.data == "arg_list" or self.ast.context.data == "arg_list":
            return
        scope = self.ast.create_sub_scope(payload=ArgListPayload())
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def after_visit_arg_list(self, _):
        if self.ast.context.data == "arg_list":
            self.ast.jump_super()


from parser import parse_file
f = parse_file("test.funq")

a = ASTBuilder(f)
a.traverse()