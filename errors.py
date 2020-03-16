

class ErrorRegistry:
    syntax_errors = {
        "S0": lambda x: "Unexpected character '" + x + "'"
    }
    logical_errors = {
        "F0": lambda _: "Quantum variable declaration not allowed in function",
        "F1": lambda _: "Return value of function not used",
        "F2": lambda _: "Incorrect number of arguments specified to function",
        "F3": lambda x: "Argument '" + x + "' passed to function has invalid type",
        "F4": lambda x: "Function name '" + x + "' is identical to a previously declared function name",
        "R0": lambda x: "Region name '" + x + "' is identical to a previously declared region name",
        "C0": lambda x: "",
        "C1": lambda x: "",
        "Q0": lambda _: "Expected quantum type in quantum variable declaration",
        "Q1": lambda x: "Quantum variable '" + x + "' allocates more qubits than allowed by the region",
        "Q2": lambda x: "Quantum variable name '" + x + "' is identical to a previously declared quantum variable",
        "Q3": lambda x: "Quantum variable name '" + x + "' is identical to a previously declared classical variable",
        "Q4": lambda x: "Quantum variable slice indexes '" + x[0] + "' to '" + x[1] + "' are out of bounds",
        "Q5": lambda x: "Quantum variable index '" + x + "' is out of bounds"
    }

    @staticmethod
    def get_error(code: str, info: str) -> str:
        if code in ErrorRegistry.syntax_errors:
            return ErrorRegistry.syntax_errors[code](info)
        elif code in ErrorRegistry.logical_errors:
            return ErrorRegistry.logical_errors[code](info)
        else:
            raise Exception("Unknown error code: " + code)


class CompilerError(Exception):
    def __init__(self, error_code, info, line=1):
        super().__init__()
        self.error_code = error_code
        self.line = line
        self.info = info

    def __repr__(self):
        _repr = "\n"
        msg = ErrorRegistry.get_error(self.error_code, self.info)
        header = "Error at line " + str(self.line) + ":"
        length = max(len(header) + 2, len(msg) + 3)
        header_spacing = length - (len(header) + 1)
        msg_spacing = length - (len(msg) + 2)
        _repr += "-" * length + "\n"
        _repr += header + " " * header_spacing + "|\n"
        _repr += msg + "." + " " * msg_spacing + "|\n"
        _repr += "-" * length + "\n"
        return _repr

    def __str__(self):
        return self.__repr__()

