class ErrorRegistry:
    """
    A static class that stores and generates errors.
    """
    syntax_errors = {
        "S0": lambda x: "Unexpected token, was expecting one of: " + x
    }
    logical_errors = {
        "V0": lambda x: "Variable '" + x + "' is not defined",
        "T0": lambda x: "Typename '" + x + "' does not name a valid type",
        "F0": lambda _: "Only function calls are allowed in function",
        "F1": lambda _: "Recursion not allowed in function",
        "F2": lambda _: "Incorrect number of arguments specified to function",
        "F3": lambda x: "Incorrect type for argument '" + x[0] + "' of function '" + x[1] + "'. \
Expected type '" + x[2] + "', got '" + x[3] + "'",
        "F5": lambda x: "Function name '" + x + "' is identical to a previously declared function name",
        "F6": lambda _: "Type of function argument can only be a constant or qubit",
        "F7": lambda x: "At least one quantum argument is required for function '" + x + "'",
        "F8": lambda x: "Function '" + x + "' is not defined",
        "R0": lambda x: "Region name '" + x + "' is identical to a previously declared region name",
        "R1": lambda x: "Quantum variable '" + x[0] + "' allocates more qubits than allowed by the region '" + x[1] + "'",
        "R1N": lambda x: "Quantum variable '" + x[0] + "' allocates more qubits than allowed by the region '" + x[1]
        + "'. Note that it is possible the limit was surpassed because you initialized at least one non-zero classical "
        + "register, which requires one qubit",
        "C0": lambda x: "Classical variable name '" + x + "' is identical to a previously declared variable",
        "C3": lambda x: "Classical variable slice indexes '" + str(x[0]) + "' to '" + str(x[1]) + "' are out of bounds",
        "C4": lambda _: "Expected classical type in classical variable declaration",
        "C5": lambda _: "Classical expression does not match variable type",
        "C6": lambda _: "Cannot perform operation on classical register",
        "Q0": lambda _: "Expected quantum register type in quantum variable declaration",
        "Q1": lambda x: "Quantum variable name '" + x + "' is identical to a previously declared variable",
        "Q2": lambda x: "Quantum variable slice indexes '" + str(x[0]) + "' to '" + str(x[1]) + "' are out of bounds",
        "Q3": lambda x: "Quantum variable index '" + str(x) + "' is out of bounds",
        "Q5": lambda _: "Quantum variable has already been measured, and cannot be measured again",
        "Q6": lambda _: "Quantum variable cannot be used after being measured",
        "Q7": lambda _: "Cannot perform classical operation on quantum variable",
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
    """
    A specific type of exception that represents an error that occurs as a result of invalid language use.
    Since all errors come from a certain element of the input code, each error will have a specific line
    and column of occurrence.
    """
    def __init__(self, error_code, line, column, info=""):
        super().__init__()
        self.error_code = error_code
        self.line = line
        self.column = column
        self.info = info

    def __repr__(self):
        _repr = "\n"
        msg = ErrorRegistry.get_error(self.error_code, self.info)
        header = "Error at line " + str(self.line) + ", column " + str(self.column) + ":"
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

