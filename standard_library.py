
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
    def generate_instruction_for(function_name, arguments):
        _func = StandardLibrary.functions[function_name]
        # TODO
        pass
