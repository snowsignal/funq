from lark import Visitor
from generation import State

class Resolver:
    def __init__(self, state):
        self.marked_nodes = []
        self.state = state
    def mark(self, node):
        self.marked_nodes.append(node)
    def resolve_nodes(self):
        for node in self.marked_nodes:
            pass


class Marker(Visitor):
    def __init__(self, resolver: Resolver, state: State):
        self.resolver = resolver
        self.state = state

    def expr(self, tree):
        pass
