class Output:
    program_header = """// Generated by the Funq compiler
OPENQASM 2.0;
include "qelib1.inc";
"""

    @staticmethod
    def generate_output(programs: dict, gates: dict):
        files = []
        for name in programs.keys():
            program = programs[name]
            comment_header = (
                "// Program: "
                + name
                + ", "
                + str(program.qubits)
                + " qubits\n"
                + Output.program_header
            )
            gates_required = {
                k: v for k, v in gates.items() if k in program.dependencies
            }
            for n in gates_required.keys():
                gate = gates_required[n]
                comment_header += gate.emit() + "\n"
            program = comment_header + program.emit()
            files.append((name, program))
        return files
