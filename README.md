# OPoly
Polyhedral compilation library for automatic code parallelization with OpenMP written in python.

## Dependencies

Python 3.9+ is required in order to use OPoly and to install it.

The python dependecies are included in the installation with `pip` and are listed here:
- [numpy](https://github.com/numpy/numpy) (>=1.19)
- [sympy](https://github.com/sympy/sympy) (>=1.7)
- [pymzn](https://github.com/paolodragone/pymzn) (>=0.18.3)

### Minizinc

The only non-python dependency which you have to take care of is the [Minizinc](https://www.minizinc.org/) CLI tool that is used to model and solve the constraint programming problems of the polyhedral approach. The easiest way to install MiniZinc is to download the MiniZincIDE package, which contains both the MiniZinc binaries and several solvers. To install it, follow [this](https://www.minizinc.org/doc-2.5.0/en/installation.html) guide. After installation, be sure that the executables are set in your `PATH` environment variable. One way to make sure about this is to try to execute the `minizinc` command from the console.

## Installation

The recommended way to install OPoly is to install it with `pip` from the [PyPI](https://pypi.org/project/opoly/) repository:

```
pip install opoly
```

You can also install OPoly from the source code available on [GitHub](https://github.com/GiackAloZ/OPoly) also with `pip`:
```
pip install .
```
or the old way:
```
python setup.py install
```

*Note*: consider using a `virtualenv` or a `conda` environment to install OPoly into.

## Usage

After installing OPoly, you will have access to the command line tool `opoly`. This script reads a file containing code that needs to be parallelized. The code must be given in a properly formatted, pseudocode language that will be described later in this section.

The script will parse this file, detect the loop-carried dependencies and perform the polyhedral optimization using the method described by Lamport in his famous article [*The Parallel Execution of DO Loops*](https://www.microsoft.com/en-us/research/uploads/prod/2016/12/The-Parallel-Execution-of-DO-Loops.pdf).

The script will then generate the parallelized version of the code in the same pseudocode language or in C syntax, adding OpenMP directives where needed.

The most common usage of the `opoly` tool is to read a file containing the nested loop(s) that needs to be parallelized. Let's say that the file contains this code:
```
FOR k FROM 1 TO q {
    FOR i FROM 1 TO n-2 {
        STM a[i] = (a[i-1] + a[i] + a[i+1]) / 3.0;
    }
}
```
Let's not care too much now about the syntax of the pseudocode as it will be described later, but to get a grasp of what this code is representing, we are going to describe it in a few words.

First, there are 2 nested loops: the outer loop iterates through variable `k` that assumes integer values from `1` to `q`; the inner loop iterates through variable `i` from `1` to `n-2`. There is a statement regarding vector `a` that assigns the element in position `i` to the sum of the elements in position `i-1`, `i` and `i+1` divided by `3`, at iteration `i` of the inner loop.

We can see that this code is not parallelizable just yet, because there are loop-carried dependecies regarding the computation of certain values of vector `a`. For example, we cannot compute `a[i]` and `a[i-1]` in parallel, since one value depends on the other.

`opoly` is able to rewrite the loops in a way that the second one can be parallelized without changing the result of the computation. The pseudocode version of the rewritten code is:
```
FOR new_k FROM 3 TO n + 2 * q - 2 STEP 1 {
    FOR CONC new_i FROM fmax(1, ceil((1.0 / 2.0) * (-n + new_k + 2))) TO fmin(q, floor((1.0 / 2.0) * (new_k - 1))) STEP 1 {
        VAR k = new_i;
        VAR i = -2 * new_i + new_k;
        STM a[i] = (a[i - 1] + a[i] + a[i + 1]) / 3.0;
    }
}
```
Two new index variables are introduced: `new_k` and `new_i`. These new indexes assume values in new ranges, which alltogether form the lattice of points inside the resulting polyhedron.

The values of the original variables are recomputed inside the innermost loop with the statements:
```
...
VAR k = new_i;
VAR i = -2 * new_i + new_k;
...
```
The statement that perform the computation remains unchanged.

There are a few functions in the loop range that compute the maximum (`fmax`), minimum (`fmin`), ceiling (`ceil`) and floor (`floor`) of their arguments.

`opoly` can also rewrite the code in C syntax and add OMP directives to perform parallel loops. The C version of the rewritten code is:
```c
for(int new_k = 3; new_k <= n + 2 * q - 2; new_k++) {
    int new_i_lb = fmax(1, ceil((1.0 / 2.0) * (-n + new_k + 2)));
    int new_i_ub = fmin(q, floor((1.0 / 2.0) * (new_k - 1)));
    #pragma omp parallel for
    for(int new_i = new_i_lb; new_i <= new_i_ub; new_i++) {
        int k = new_i;
        int i = -2 * new_i + new_k;
        a[i] = (a[i - 1] + a[i] + a[i + 1]) / 3.0;
    }
}
```
Notice that the values of the lower and upper bounds of the inner loop are computed before the loop statement in this version. The result is a more readable code, not impacting performance.

Suppose that the file containing the input code is named `example1.psc`, then the command required to generate the parallel code is:
```
opoly example1.psc
```
By default, `opoly` will output in the standard output the generated code in C syntax (with OMP directives).
To output the code in pseudocode syntax, one can use the `-f` or `--format` option to specify the format of the resulting code to `PSEUDO`:
```
opoly example1.psc -f PSEUDO
```
The `-o` or `--output` argument can be used to specify a custom file in which the resulting code should be written, instead of the standard output:
```
opoly example1.psc -o omp-example1.c
```

### Pseudocode syntax

We will now describe the syntax of the pseudocode.

We must first define the difference between indexes, parameters and vectors:
- an *index* is a for loop index varialbe (eg. `i` or `k` in the examples above).
- a *parameter* is every variable in the program for which the value is know at the time of execution and its value does not change during the execution (eg. `q` or `n` in the examples above).
- a *vector* is a multi-dimensional variable that appears in assigments and is used to store computation results (eg. `a` in the examples above).

We will discuss more about the restrictions each variable has in order to extract the dependecies and rewrite the loops later in this section.

The for loop statement syntax is:

> **FOR** *var_idx* **FROM** *lb_const* **TO** *ub_expr* {
> 
> &emsp; *loop_body*
> 
> }

where:
- *var_idx* is the name of the variable representing the loop's index (eg. `i`, `j` or `k`).
- *lb_const* is a positive constant integer (eg. `0`, `1` or `42`) representing the initial value of the index variable.
- *ub_expr* is an expression representing the last value of the index variable. There are 3 possible kind of expression that can be written:
    - a positive constant integer
    - a parameter name
    - a two-term expression with a parameter name, an operator (`+` or `-`) and a constant expression (eg. `n-2`).
- *loop_body* are other statements (possibly for loops) contained in the loop body. If there are nested loops, the loops must be perfectly nested, which means that no other statements must be present in the loop body containing another for loop.

*NOTE*: each index variable name must be unique for every for loop.

The assigment statement syntax is:

> **STM** *left_term* **=** *right_term* **;**

where:
- *left_term* is a vector expression, indexed by one or more index variables (eg. `a[i]`). A two-term expression can be present as index, but it must contain only one index variable, an operator (`+` or `-`) and a constant integer (eg. `a[i+2]`).
- *right_term* is a general expression containing vectors, parameters, indexes and constants.

*NOTE*: please note the `;` at the end of the statement.

The vector expression syntax is:

> *vector_name*__[__*index_expr*__]__...

where:
- *vector_name* is the name of the vector (eg. `a`)
- *index_expr* is an expression containing only one index variable (eg. `i`, `i+1`, `i-2`, etc...). There can be multiple indexes expression, one for each vector's dimension.

For example, a correct vector expression is `a[i+1][j-1]` and an incorrect vector expression is `a[i+j][j]` because `i` and `j` are both present in the first dimension index of the vector.

Also, if vectors with the same name cannot be indexed with different index variables or in different order. For example, if `x[i][j]` is present, `x[j][i]` cannot be present as well as `x[i]`.

A general expression is a list of other expression with an operator in between each of them. For example, `a + 1` is an expression of two terms `a` and `1` with an operator `+` in between them. In general, an expression can be described by the following syntax:

> *expr* [*op* *other_expr*]...

where:
- *expr* and *other_expr* are expressions
- *op* is an operator. Supported operators are `+` (addition), `-` (subtraction), `*` (multiplication) and `/` (division).

There can be also round brackets `()` around an expression.

An example of a correct expression is:
```
a + v[i] * (1 - v[i-1]) / 3.0
```
