from lark import Lark, Tree, Transformer, Visitor, Token

GRAMMAR_FILE = "grammar.lark"

class ASTTransformer(Transformer):
    def __init__(self):
        super().__init__()
        pass

    def f_ident(self, tree: Tree) -> Tree:
        return Tree(("f_ident", tree[0].children[0].value), [])

    def v_ident(self, tree: Tree) -> Tree:
        return Tree(("v_ident", tree[0].children[0].value), [])

    def type(self, tree: Tree) -> Tree:
        return Tree(("type", tree[0].value), [])

    def arg_list(self, tree: Tree) -> Tree:
        a_list = []
        for t in tree:
            a_list.append(tuple(t.children))
        return Tree(("arg_list", a_list), [])



def grammar() -> str:
    global GRAMMAR_FILE
    with open(GRAMMAR_FILE) as f:
        return "\n".join(f.readlines())


def parse_file(f_name: str) -> Tree:
    with open(f_name) as f:
        contents = "\n".join(f.readlines())
        l = Lark(grammar(), parser='lalr')
        return l.parse(contents)


if __name__ == "__main__":
    t = parse_file("test.funq")
    print(t)
    transformer = ASTTransformer()
    t = transformer.transform(t)
    print(t)
