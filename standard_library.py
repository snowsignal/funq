from payloads import *

class StandardLibrary:
    """
    A static registry of functions that are standard across all Funq programs.
    """
    functions = {
        "hadamard": "h",
        "cx": "cx",
        "not": "x",
        "y": "y",
        "z": "z",
        "swap": "swap",
        "ccx": "ccx",
        "rx": "rx",
        "ry": "ry",
        "rz": "rz",
    }

    args = {
        "hadamard": [("target", "Q")],
        "cx": [("control", "Q"), ("target", "Q")],
        "not": [("target", "Q")],
        "y": [("target", "Q")],
        "z": [("target", "Q")],
        "swap": [("first", "Q"), ("second", "Q")],
        "ccx": [("control1", "Q"), ("control2", "Q"), ("target", "Q")],
        "rx": [("rotation", "Const"), ("target", "Q")],
        "ry": [("rotation", "Const"), ("target", "Q")],
        "rz": [("rotation", "Const"), ("target", "Q")]
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
