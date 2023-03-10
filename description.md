# Project #1 - Optimizing Python Code

<img src="images/Serpiente_alquimica.jpg?raw=True" align="right" width="10%"/>

In this project you will write Python code that optimizes Python code.
We name this project _Ouroboros_ after [the ancient symbol](https://en.wikipedia.org/wiki/Ouroboros)
showing a snake eating its own tail.

You will optimize code in two specific ways: removing unnecessary computations and hoisting loop invariants.

## Unnecessary Computations
As we saw in class, compilers often times perform code transformations to make the generated native code more efficient.
The compiler built into the standard Python implementation, CPython, however, misses out on fairly basic optimizations.
For example, consider `func()` below, which performs a number of (unnecessary) computations to only return a constant:
```Python
def func():
   x = 10
   for i in range(10):
       x += .5
   a = x + 7 / .55
   return 42
```
Ideally the compiler would detect that those computations are unnecessary and simply return the constant.
We can see what it generated by asking Python to disassemble the function:
```
$ python3.11
Python 3.11.1 (main, Dec 23 2022, 09:28:24) [Clang 14.0.0 (clang-1400.0.29.202)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> def func():
...    x = 10
...    for i in range(10):
...        x += .5
...    a = x + 7 / .55
...    return 42
... 
>>> import dis
>>> dis.dis(func)
  1           0 RESUME                   0

  2           2 LOAD_CONST               1 (10)
              4 STORE_FAST               0 (x)

  3           6 LOAD_GLOBAL              1 (NULL + range)
             18 LOAD_CONST               1 (10)
             20 PRECALL                  1
             24 CALL                     1
             34 GET_ITER
        >>   36 FOR_ITER                 7 (to 52)
             38 STORE_FAST               1 (i)

  4          40 LOAD_FAST                0 (x)
             42 LOAD_CONST               2 (0.5)
             44 BINARY_OP               13 (+=)
             48 STORE_FAST               0 (x)
             50 JUMP_BACKWARD            8 (to 36)

  5     >>   52 LOAD_FAST                0 (x)
             54 LOAD_CONST               3 (12.727272727272727)
             56 BINARY_OP                0 (+)
             60 STORE_FAST               2 (a)

  6          62 LOAD_CONST               4 (42)
             64 RETURN_VALUE
>>> 
```
What you see above is a [disassembly](https://docs.python.org/3/library/dis.html) of Python's [_bytecode_](https://en.wikipedia.org/wiki/Bytecode).
Bytecode instructions are similar to processor instructions: it's a _Pseudo-ISA_.
CPython compiles source code to bytecode, which it then executes.
As we can see above, all the unnecessary computations were retained.
A function that simply returns a constant is much simpler:
```
>>> def func():
...     return 42
... 
>>> dis.dis(func)
  1           0 RESUME                   0

  2           2 LOAD_CONST               1 (42)
              4 RETURN_VALUE
>>> 
```

## Hoisting Loop Invariants
Compilers commonly also move portions of the code around to optimize for a goal,
such as faster execution or smaller executable output.
For example, a loop might include a computation that doesn't really need to be
performed in each iteration, such as `x + y` in the `for` below:
```Python
def fill_sum(a, x, y):
   for i in range(len(a))
       a[i] = x + y
```
For best performance, that expression should be moved out of the loop, such as in
```Python
def fill_sum(a, x, y):
   tmp = x + y
   for i in range(len(a))
       a[i] = tmp
```
We say that computation is _hoisted_ out of the loop.

## The Project

Compilers typically perform optimizations on some kind of _intermediate representation_ (IR).
They generate such an IR from source code, and generate the executable code from the IR.
In Python, the most readily available IR is the [_Abstract Syntax Tree_](https://docs.python.org/3/library/ast.html) (AST),
which it generates after parsing.

In this project, you will write a Python script, named `ouroboros.py`, that exposes three
functions that given an AST, return an optimized AST:
- `remove_useless()` removes unnecessary computations
- `hoist_invariants()` hoists invariants out of loops
- `optimize()` repeats the two steps above until neither can further optimize the AST.

The functions may also modify in the AST in-place, if you prefer.

You should implement your optimizations _conservatively_: only change code in ways you are
certain it is safe to change.

### Removing Unnecessary Computations
You can remove unnecessary computations by processing the AST in a similar way as a mark-and-sweep garbage collector.
For each portion of code such as a function or module, first process its statements from last to first, marking
the statements (and variables) that are useful.
Then go through that portion of the AST once again, sweeping for unmarked statements, removing them.
For example:
```Python
def func():
   x = 10
   y = 2
   a = x + 7 / .55
   return x+y
```
In this function:
- the `return` is useful, and it also marks the variables `x` and `y` as useful;
- the assignment to `a` is not useful, since `a` hasn't been marked useful;
- the assignments to `y` and `x` are useful, since those variables were marked useful.

Loop statements such as `for` and `while` will need special treatment since the statements at the
beginning of the loop can also be reached after the last statement executes (if it loops around).

### Hoisting Expressions
Sometimes it is possible to hoist an entire statement out of a loop, such as in
```Python
def fill_sum(a, x, y):
   for i in range(10)
       z = x + y
       ...
```
which can be transformed to
```Python
def fill_sum(a, x, y):
   z = x + y
   for i in range(10)
       ...
```

When the left hand side of an assignment depends on the loop variables, it may not be
hoisted, but it may still be possible to hoist the expression on the right hand side.
As the example shown before, this program
```Python
def fill_sum(a, x, y):
   for i in range(len(a))
       a[i] = x + y
```
can be optimized as
```Python
def fill_sum(a, x, y):
   __o_tmp_3 = x + y
   for i in range(len(a))
       a[i] = __o_tmp_3
```
To simplify writing tests that work across implementations, please create any such
temporary variables as `__o_tmp_N`, where `N` is the line number of the original expression.

### Python variable scopes
Variables can exist in a number of different _scopes_.
In Python, variables in outer scopes are generally visible within inner ones, but the scope of a variable
is normally given by the code that _assigns_ a value to it.
For example, in
```Python
x = 42
def foo():
    print(x)

foo()
```
the variable `x` is defined globally, and is visible within `foo()`.
Running this program prints out the number 42.
If the program is changed, however, to
```Python
x = 42
def foo():
    x = x + 10
    print(x)

foo()
```
then Python emits an `UnboundLocalError`, saying that the variable `x` was referenced before assignment.
This is because **two** different variables `x` were defined: one global, and another
within `foo`.

You can modify a variable's scope using `global` and `nonlocal` statements.
If example above was changed to:
```Python
x = 42
def foo():
    global x
    x = x + 10
    print(x)

foo()
```
then Python would no longer emit that error, but would print out the number 52.

Python ASTs include variable names within `ast.Name` objects, as well as in a few other items.
In this project you will need to keep track of scoping and assignment functions to correctly
identify which variables are meant.

Note that function names are variables, too!
The `def` statement functions a bit like an assignment, defining a variable with the function's name.
For example, the code below defines a global function `bar()`.
```Python
def foo():
    global bar
    def bar():
        print("Hello, world!")
        
foo()
bar()
```

For further reading you may want to look up this [example](https://docs.python.org/3/tutorial/classes.html#scopes-and-namespaces-example)
from the Python documentation, or [this article](https://realpython.com/python-scope-legb-rule) from realpython.com.

### Function Purity
Functions that have side effects such as I/O, writing or even reading from global variables or
other state make these optimizations more difficult.
For example, it might seem that the code below
```Python
for i in range(10)
    x = f(10)
```
could be optimized to
```Python
x = f(10)
```
but that would be incorrect if `f()` had side effects, such as in
```Python
g = 0
def f(p):
    g += 1
    return p
```

Functions that only depend on their parameters and that have no side effects are
named [_pure_](https://en.wikipedia.org/wiki/Pure_function).
In this project you do **not** need to implement a function purity analysis, but you can
choose to do so for additional credit.
If you do not implement function purity analysis, instead considering all function calls
potentially impure, you are still required to handle "known pure" [built-in functions](https://docs.python.org/3/library/functions.html)
such as `range()` and `len()` separately, so that code such as
```Python
for i in [1,2,3]:
   x = len(a)
```
can be optimized to
```Python
x = len(a)
```

## Testing
You should write automated tests using [pytest](https://docs.pytest.org/) for your optimizer,
such as the one below:
```Python
import ast
from ouroboros import optimize

def test_instructions_example():
    t = ast_parse("""
       def func():
           x = 10
           for i in range(10):
               x += .5
           a = x + 7 / .55
           return 42
    """)

    print(ast.dump(t, indent=4))
    t = optimize(t)

    assert ast_unparse(t) == clean("""
       def func():
           return 42
    """)
```
The test parses a portion of Python code from a string, invokes the `optimize` function,
turns the AST back into source code, and compares the result.
If the test fails, the output will include a dump of the AST (before your changes; you can add other output as needed).
If you save your tests as `test_optimize.py`, you could run them as
```
python3 -m pytest -vv
```

The file [test_minimum.py](test_minimum.py) contains a minimum set of tests that your
implementation should pass.

You are also welcome to share your tests with other groups (but **not** your optimizer code!).

## Other details

- please use Python 3.10 or 3.11;
- please identify, in your GitHub project repository, what each team member worked on;
- all team members are expect to contribute equally;
- it is a good idea to commit (and push) frequently;
- please keep your repositories private;
- you may **not** use ChatGPT or other generative AI models in this project;
- the due date is April 7.
