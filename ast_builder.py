from lark import Token, Tree
from payloads import ArgListPayload, ArgPayload, AssignmentPayload, BitPayload, BlockPayload, BoolOpPayload, CallListPayload, ClassicalDeclarationPayload, ClassicalLiteralPayload, FIdentPayload, FunctionCallPayload, FunctionPayload, IfPayload, MeasurementPayload, OpPayload, QuantumDeclarationPayload, QuantumIndexPayload, QuantumLiteralPayload, QuantumSlicePayload, RIdentPayload, RegionPayload, TypePayload, UIntPayload, VIdentPayload
from scope import AST
from visitor import Visitor
from math import ceil


def token_to_str(t: Token) -> str:
    return t.value


def get_line_column(t: Tree) -> (int, int):
    return ceil(t.meta.line / 2), t.meta.column


class ASTBuilder(Visitor):
    def __init__(self, syntax_tree: Tree):
        super().__init__(syntax_tree)
        self.ast = AST()

    def insert_new_scope(self, tree, payload=None):
        line, column = get_line_column(tree)
        self.ast.create_sub_scope(line, column, payload=payload)

    def insert_new_scope_and_jump(self, tree, payload=None):
        line, column = get_line_column(tree)
        scope = self.ast.create_sub_scope(line, column, payload=payload)
        if not self.ast.jump_to(scope.ID):
            raise Exception("could not jump to scope")

    def visit_function_def(self, t):
        self.insert_new_scope_and_jump(t, payload=FunctionPayload())

    def after_visit_function_def(self, _):
        self.ast.jump_super()

    def visit_region(self, t):
        self.insert_new_scope_and_jump(t, payload=RegionPayload())

    def after_visit_region(self, _):
        self.ast.jump_super()

    def visit_function_call(self, t):
        self.insert_new_scope_and_jump(t, payload=FunctionCallPayload())

    def after_visit_function_call(self, _):
        self.ast.jump_super()

    def visit_if(self, t):
        self.insert_new_scope_and_jump(t, payload=IfPayload())

    def after_visit_if(self, _):
        self.ast.jump_super()

    def visit_sum(self, t):
        expr = t.children[0]
        if expr.data == "product":
            return
        elif expr.data in ["add", "sub"]:
            self.insert_new_scope_and_jump(t, payload=OpPayload(expr.data))
        else:
            raise Exception("Invalid expression data")

    def after_visit_sum(self, t):
        expr = t.children[0]
        if expr.data == "product":
            return
        self.ast.jump_super()

    def visit_product(self, t):
        expr = t.children[0]
        if expr.data == "atomic":
            return
        elif expr.data in ["mul", "div"]:
            self.insert_new_scope_and_jump(t, payload=OpPayload(expr.data))
        else:
            raise Exception("Invalid expression data")

    def after_visit_product(self, t):
        expr = t.children[0]
        if expr.data == "atomic":
            return
        self.ast.jump_super()

    def visit_b_expr(self, t):
        op = t.children[0]
        if op.data in ["eq", "neq", "greater", "lesser"]:
            self.insert_new_scope_and_jump(t, payload=BoolOpPayload(op.data))
        else:
            raise Exception("Invalid boolean expression data")

    def after_visit_b_expr(self, _):
        self.ast.jump_super()

    def visit_block(self, t):
        self.insert_new_scope_and_jump(t, payload=BlockPayload())

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
        name = token_to_str(t.children[0])
        self.insert_new_scope(t, payload=TypePayload(name))

    def visit_f_ident(self, t):
        # Function identifiers and variable identifiers must be put
        # in lowercase to work in OpenQASM
        name = token_to_str(t.children[0]).lower()
        self.insert_new_scope(t, payload=FIdentPayload(name))

    def visit_v_ident(self, t):
        name = token_to_str(t.children[0]).lower()
        self.insert_new_scope(t, payload=VIdentPayload(name))

    def visit_r_ident(self, t):
        name = token_to_str(t.children[0])
        self.insert_new_scope(t, payload=RIdentPayload(name))

    def visit_uint(self, t):
        # This will always succeed since only ints are parsed in the first place.
        val = int(token_to_str(t.children[0]))
        self.insert_new_scope(t, payload=UIntPayload(val))

    def visit_call_list(self, t):
        if self.ast.context.super_scope.data == "call_list":
            self.ast.jump_super()
            return
        if self.ast.context.data == "call_list":
            return
        self.insert_new_scope_and_jump(t, payload=CallListPayload())

    def after_visit_call_list(self, _):
        if self.ast.context.data == "call_list" and not self.ast.context.super_scope.data == "call_list":
            self.ast.jump_super()

    def visit_arg(self, t):
        self.insert_new_scope_and_jump(t, payload=ArgPayload())

    def after_visit_arg(self, _):
        self.ast.jump_super()

    def visit_arg_list(self, t):
        if self.ast.context.super_scope.data == "arg_list" or self.ast.context.data == "arg_list":
            return
        self.insert_new_scope_and_jump(t, payload=ArgListPayload())

    def after_visit_arg_list(self, _):
        if self.ast.context.data == "arg_list":
            self.ast.jump_super()

    def visit_q_slice(self, t):
        self.insert_new_scope_and_jump(t, payload=QuantumSlicePayload())

    def after_visit_q_slice(self, _):
        self.ast.jump_super()

    def visit_q_lit(self, t):
        self.insert_new_scope_and_jump(t, payload=QuantumLiteralPayload())

    def visit_bit(self, t):
        v = t.children[0].value
        value = v == "1"
        self.insert_new_scope_and_jump(t, payload=BitPayload(value))

    def after_visit_bit(self, _):
        self.ast.jump_super()

    def after_visit_q_lit(self, _):
        self.ast.jump_super()

    def visit_q_declaration(self, t):
        self.insert_new_scope_and_jump(t, payload=QuantumDeclarationPayload())

    def after_visit_q_declaration(self, _):
        self.ast.jump_super()

    def visit_q_index(self, t):
        self.insert_new_scope_and_jump(t, payload=QuantumIndexPayload())

    def after_visit_q_index(self, _):
        self.ast.jump_super()

    def visit_c_lit(self, t):
        self.insert_new_scope_and_jump(t, payload=ClassicalLiteralPayload())

    def after_visit_c_lit(self, _):
        self.ast.jump_super()

    def visit_declaration(self, t):
        self.insert_new_scope_and_jump(t, payload=ClassicalDeclarationPayload())

    def after_visit_declaration(self, _):
        self.ast.jump_super()

    def visit_measurement(self, t):
        self.insert_new_scope_and_jump(t, payload=MeasurementPayload())

    def after_visit_measurement(self, _):
        self.ast.jump_super()
