

class Types:
    classical_types = {
        "Int": 32,
        "Byte": 8,
        "Bit": 1
    }
    quantum_types = ["Q"]

    @staticmethod
    def is_classical(typename):
        return typename in Types.classical_types

    @staticmethod
    def is_quantum(typename):
        return typename in Types.quantum_types

    @staticmethod
    def is_valid(typename):
        return Types.is_valid(typename) or Types.is_quantum(typename)
