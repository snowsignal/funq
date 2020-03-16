from lark import Token, Tree
#from copy import deepcopy


class TreeTraversal:
    def __init__(self, tree):
        self.tree = tree

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
            self.visit_any(t)
            func = getattr(self, "visit_" + t.data)
            func(t)
        except (AttributeError, TypeError) as e:
            if "visit_" not in str(e):
                raise e

    def _post_process_tree(self, t):
        try:
            func = getattr(self, "after_visit_" + t.data)
            func(t)
        except (AttributeError, TypeError) as e:
            print(e)
            return

    def visit_any(self, t):
        pass

    def set_source(self, tree):
        self.tree = tree


class Transformer(TreeTraversal):
    def __init__(self, tree):
        super().__init__(tree)

    def _traverse(self, t):
        if isinstance(t, Token):
            return
        t = self._transform(t)
        if t is not None:
            for i, v in enumerate(t.children):
                print(i)
                t.children[i] = self._traverse(v)
            t.children = [c for c in t.children if c is not None]
        return t

    def _transform(self, t):
        try:
            func = getattr(self, "transform_" + t.data)
            return func(t)
        except (AttributeError, TypeError) as e:
            print(e)
            return t

