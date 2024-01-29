from lark import Lark, Tree

GRAMMAR_FILE = "grammar.lark"


def grammar() -> str:
    global GRAMMAR_FILE
    with open(GRAMMAR_FILE) as f:
        return "\n".join(f.readlines())


PARSER = Lark(grammar(), parser="earley", propagate_positions=True, lexer="dynamic")


def parse_file(f_name: str) -> Tree:
    with open(f_name) as f:
        contents = "\n".join(f.readlines())
        return parse(contents)


def parse(contents: str) -> Tree:
    return PARSER.parse(contents)
