import unittest
from input_parser import parse


class TestASTBuild(unittest.TestCase):
    def setUp(self) -> None:
        self.contents_for_test = """
        region Test<5> { Q[] q1 = ^000^; }
        """

    def test_ast_builds_correctly(self):
        tree = parse(self.contents_for_test)
        # Perform verification on the tree
        self.assertTrue(len(tree.children) == 1)


if __name__ == "__main__":
    unittest.main()
