class Types:
    """
    Types is a helper static class that stores the list of builtin types:
    - The classical constant type (Const)
    - The classical register type (C[])
    - The qubit type (Q)
    - The quantum register type (Q[])
    """
    classical_types = ["Const", "C[]"]
    quantum_types = ["Q", "Q[]"]
    registers = ["C[]", "Q[]"]

    """
    This checks that the typename passed is a classical type
    """
    @staticmethod
    def is_classical(typename):
        return typename in Types.classical_types

    """
    This checks that the typename passed is a quantum type.
    """
    @staticmethod
    def is_quantum(typename):
        return typename in Types.quantum_types

    """
    This checks that the typename passed is a register type.
    This means it cannot be used as a function parameter.
    """
    @staticmethod
    def is_register(typename):
        return typename in Types.registers

    """
    This checks that the typename passed is valid (either a classical or quantum type).
    """
    @staticmethod
    def is_valid(typename):
        return Types.is_classical(typename) or Types.is_quantum(typename)
