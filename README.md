# Funq

Funq is a simple, straightforward quantum language. It compiles to OpenQASM and can be run
directly on a quantum computer.

## Installation

To use Funq, you will need Python 3.5 or later, as well as the pip package manager.
To install dependencies, simply type the command:
```bash
pip install -r requirements.txt
```
while in the project folder.

## Learn Funq

There are two fundamental concepts in Funq, *regions* and *functions*. Regions are
blocks of code that represent quantum programs, and functions are procedures that
can be called from these regions.

There are several built-in functions, such as `hadamard` and `not`. Functions usually
take qubits as arguments, but can also take constants.

An important distinction between functions in Funq and functions in other languages is that
functions don't return anything. This is because all values are passed by reference, and
modifications to qubits are made in-place by function calls.

### Types

There are four types in Funq: `Q`, `Q[]`, `Const`, and `C[]`. `Q` is the qubit type, `Q[]` is
the quantum register type, `Const` is the constant classical value type, and `C[]` is the
classical bit register. Only `Q` and `Const` can be used as function arguments, and only
`Q[]`, `C[]`, and `Const` can be explicitly declared. `Q` is the result of taking an index
or slice of a quantum register.

### Variable declaration
```
// This declares a constant classical variable
Const value = 10;
Const value2 = value + 20 * 2;

// This declares a quantum register with three qubits, each set to zero.
Q[] register = ^000^;

// This declares a classical register with five qubits, two of which have
// been set to one.
C[] c_register = #01001;
```

### Function declaration and usage

Functions work very differently from regions. Inside of a function body, you can
only call other functions. All variable declaration and such must take place in
a region. Here is an example of a function that would not compile, for multiple
reasons:
```
// This line would not work, since 'a' is a register and not a qubit.
function BadFunction(c: Const, a: Q[]) {
  // This statement would not work, since if statements cannot be in a function
  if c == 5 {
    // This statement would not work either, since functions cannot be recursive!
    BadFunction (c, a);
  }
}
```

Here is an example of a working function:
```
function GoodFunction(c: Const, q: Q) {
  x(q);
  universal(c, 0, 0, q);
}
```

Functions can be used across regions. Funq also comes with a small set of
pre-defined functions in its standard library. These are:
```
not (Q) -> NOT gate for a qubit
cx (Q, Q)  -> Controlled NOT gate, with the first qubit acting as control.
hadamard (Q) -> Quantum Hadamard gate
x (Q) -> Quantum Pauli-X gate
y (Q) -> Quantum Pauli-Y gate
z (Q) -> Quantum Pauli-Z gate
swap (Q, Q) -> Swaps the values of two qubits
ccx (Q, Q, Q) -> CCNOT gate, also known as Toffoli gate.
rx (C, Q) -> Rotational-X gate.
ry (C, Q) -> Rotational-Y gate.
rz (C, Q) -> Rotational-Z gate.
```

### Indexing and slicing

Quantum registers can be indexed or sliced to extract qubits, which can be passed to functions.

When a quantum register is 'sliced', the function in which it is sliced is called once
for each qubit in the slice. There can only be one slice in each function call within Funq.

Here is an example of indexing and slicing:
```
Q[] q = ^000^;
// This will call the hadamard gate three times, once for each qubit in the slice
hadamard (q[0:2]);
// This performs the NOT gate on the first qubit only
not (q[0]);
// This performs the Controlled-NOT gate twice, once for the second qubit and once
// for the third qubit in the register.
cx (q[0], q[1:2]);
```

### Measurement

Quantum registers can be measured, and the results stored in a classical register.
After part of a quantum register has been measured, it cannot be used again.

Here is an example of measurement:
```
C[] reg = #000;
Q[] q_reg = ^000^;
hadamard(q_reg[0:2]);
reg[0:] <- q_reg[0:2];
```

The last statement is the measure statement. This statement says to measure a slice of
the quantum register and store it in the classical register, starting at index 0.

### Running the compiled OpenQASM

Valid OpenQASM code can be run directly on [IBM's website](quantum-computing.ibm.com).
Register for an account, go to Circuit Composer, create a new circuit, go to the code
tab, and paste in the generated code. Please note that the website's transpiler does
not fully adhere to the OpenQASM language specification, so errors may occur
due to unimplemented features.

Please let me know of any issues or confusing problems you run into via the Github
Issues tab. Enjoy programming in Funq!

### Authors

This code was written and published by Jackson Lewis. All rights reserved.
