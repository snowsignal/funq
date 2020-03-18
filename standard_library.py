from payloads import *

class StandardLibrary:
    functions = {
        "not": "NOT",
        "hadamard": "h",
        "cx": "cx",
        "x": "x",
        "y": "y",
        "z": "z",
        "swap": "swap",
        "ccx": "ccx",
        "rx": "rx",
        "ry": "ry",
        "rz": "rz",
    }

    args = {
        "not": [("target", "Q")],
        "hadamard": [("target", "Q")],
        "cx": [("control", "Q"), ("target", "Q")],
        "x": [("target", "Q")],
        "y": [("target", "Q")],
        "z": [("target", "Q")],
        "swap": [("first", "Q"), ("second", "Q")],
        "ccx": [("control1", "Q"), ("control2", "Q"), ("target", "Q")],
        "rx": [("rotation", "C"), ("target", "Q")],
        "ry": [("rotation", "C"), ("target", "Q")],
        "rz": [("rotation", "C"), ("target", "Q")]
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
