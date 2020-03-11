
class StandardLibrary:
    functions = {
        "not": "NOT",
        "universal": "U",
        "hadamard": "h"
    }

    @staticmethod
    def is_standard(function_name):
        return function_name in StandardLibrary.functions

    @staticmethod
    def get_standard_name(function_name):
        return StandardLibrary.functions[function_name]
