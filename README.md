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
cx (Q, Q)  -> Controlled NOT gate, with the first qubit acting as control.
hadamard (Q) -> Quantum hadamard gate

```