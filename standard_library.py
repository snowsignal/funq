from payloads import *

class StandardLibrary:
    functions = {
        "not": "NOT",
        "universal": "U",
        "hadamard": "h",
        "cx": "cx",
        "x": "x",
        "y": "y",
        "z": "z"
    }

    args = {
        "not": [("arg", "Q")],
        "universal": [("c1", "Const"), ("c2", "Const"), ("c3", "Const"), ("arg", "Q")],
        "hadamard": [("arg", "Q")],
        "cx": [("control", "Q"), ("arg", "Q")],
        "x": [("arg", "Q")],
        "y": [("arg", "Q")],
        "z": [("arg", "Q")]
    }

    @staticmethod
    def is_standard(function_name):
        return function_name in StandardLibrary.functions

    @staticmethod
    def get_standard_name(function_name):
        return StandardLibrary.functions[function_name]

    @staticmethod
    def get_standard_args(function_name):
        return StandardLibrary.args[function_name]
