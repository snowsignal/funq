from lark import Token, Tree
from copy import deepcopy


class TreeTraversal:
    def __init__(self, tree):
        self.tree = deepcopy(tree)

    def _traverse(self, t):
        return t

    def traverse(self):
        self.tree = self._traverse(self.tree)


class Visitor(TreeTraversal):
    def __init__(self, tree):
        super().__init__(tree)

    def _traverse(self, t):
        if isinstance(t, Token):
            return
        self._process_tree(t)
        for child in t.children:
            self._traverse(child)
        self._post_process_tree(t)
        return t

    def _process_tree(self, t):
        try:
            func = getattr(self, "visit_" + t.data)
            func(t)
        except (AttributeError, TypeError) as e:
            print(e)
            return

    def _post_process_tree(self, t):
        try:
            func = getattr(self, "after_visit_" + t.data)
            func(t)
        except (AttributeError, TypeError):
            return


class Transformer(TreeTraversal):
    def __init__(self, tree):
        super().__init__(tree)

    def _traverse(self, t):
        if isinstance(t, Token):
            return
        for i in range(0, len(t.children)):
            t.children[i] = self._traverse(t.children[i])
        t = self._transform(t)
        return t

    def _transform(self, t):
        try:
            func = getattr(self, "transform_" + t.data)
            return func(t)
        except (AttributeError, TypeError):
            return t

