from lark import Lark, Tree

GRAMMAR_FILE = "grammar.lark"


def grammar() -> str:
    global GRAMMAR_FILE
    with open(GRAMMAR_FILE) as f:
        return "\n".join(f.readlines())


def parse_file(f_name: str) -> Tree:
    with open(f_name) as f:
        contents = "\n".join(f.readlines())
        l = Lark(grammar(), parser='lalr', propagate_positions=True)
        return l.parse(contents)
