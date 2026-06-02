# E to Python — A Friendly Bridge

If you learned E and you want to try Python, **congratulations**: you already
know 80% of what you need. This document shows you the mapping.

E and Python are very similar in *ideas*. The differences are mostly in
*spelling*. Once you get used to Python's spelling, you'll see the same
programming thinking underneath.

## The big shift in one sentence

> E hides a lot of Python's syntax tax. You already know the **logic**.
> Now you learn the **spelling**.

What that means in practice: in E you write `say "Hello"` and the program
prints `Hello`. In Python you write `print("Hello")`. Same idea, different
spelling.

## Hello, world

| E | Python |
|---|--------|
| `say "Hello, world!"` | `print("Hello, world!")` |

The biggest single change: in Python, `print` is a *function*, so it
**always** uses parentheses. There is no bare `say` shortcut.

## Variables

| E | Python |
|---|--------|
| `let name be "Alice"` | `name = "Alice"` |
| `let age be 25` | `age = 25` |

In Python, you don't need a `let` keyword — just type the name, `=`, and
the value. One less word to remember, but a tiny bit more risk: you can
accidentally re-assign a variable when you meant to compare it.

## Strings and joining them

| E | Python |
|---|--------|
| `"hello"` or `'hello'` or `` `hello` `` | `"hello"` or `'hello'` (no backticks) |
| `say "Hi, " , name` | `print("Hi, " + name)` or `print(f"Hi, {name}")` |

The **comma** in E is the **plus** in Python (for string concat). Python
also has a fancy way called f-strings (the `f"..."` form) that lets you
embed variables inside the string with `{}`. That's super useful once
you get used to it.

## Numbers and math

| E | Python |
|---|--------|
| `5 plus 3` | `5 + 3` |
| `10 minus 4` | `10 - 4` |
| `6 times 7` | `6 * 7` |
| `10 divided by 3` | `10 / 3` (gives `3.333...`) |
| `10 mod 3` | `10 % 3` |
| `2 times (3 plus 4)` | `2 * (3 + 4)` |

Python uses the math symbols you already know. The catch: Python
distinguishes between `int` (whole numbers like `5`) and `float`
(decimal numbers like `3.14`). Division `/` always gives a float, even
when the result is a whole number. Use `//` for integer division.

## Comparisons

| E | Python |
|---|--------|
| `x is equal to 5` | `x == 5` |
| `x is not equal to 5` | `x != 5` |
| `x is greater than 5` | `x > 5` |
| `x is less than 5` | `x < 5` |
| `x is greater than or equal to 5` | `x >= 5` |
| `x is less than or equal to 5` | `x <= 5` |

In Python, **two equals signs** `==` mean "compare for equality". **One
equal sign** `=` is for assignment. This trips up everyone at first.

## Booleans (true/false)

| E | Python |
|---|--------|
| `true` | `True` |
| `false` | `False` |
| `nothing` | `None` |
| `x and y` | `x and y` |
| `x or y` | `x or y` |
| `not x` | `not x` |

**Watch out:** `True`, `False`, and `None` are **capitalized** in Python
and **lowercase** in E. The single biggest typo you can make in Python
is writing `true` (Python will say it doesn't know what that is).

## Making choices: if / else

| E | Python |
|---|--------|
| `if age is greater than 18 then`<br>`    say "adult"`<br>`else`<br>`    say "kid"`<br>`end` | `if age > 18:`<br>`    print("adult")`<br>`else:`<br>`    print("kid")` |

The **biggest gotcha** in Python: instead of `end`, you use **indentation**.
Lines that start with the same number of spaces are part of the same
block. Four spaces is the standard. The line that ends a block is the
first one that's *less* indented than the line before it.

**Tip:** if your Python code "looks right but doesn't run", the first
thing to check is whether the indentation matches.

You can also chain `else if` in Python, but it's written `elif`:

| E | Python |
|---|--------|
| `else if x is 1 then` | `elif x == 1:` |

## Loops

| E | Python |
|---|--------|
| `repeat 5 times`<br>`    say "hi"`<br>`end` | `for i in range(5):`<br>`    print("hi")` |
| `while x is less than 10`<br>`    say x`<br>`    let x be x plus 1`<br>`end` | `while x < 10:`<br>`    print(x)`<br>`    x = x + 1` |
| `for each fruit in fruits`<br>`    say fruit`<br>`end` | `for fruit in fruits:`<br>`    print(fruit)` |

`range(5)` in Python is a magic thing that gives you the numbers
`0, 1, 2, 3, 4`. If you want `1` to `5`, use `range(1, 6)`.

## Lists

| E | Python |
|---|--------|
| `let fruits be ["apple", "banana"]` | `fruits = ["apple", "banana"]` |
| `fruits at 0` | `fruits[0]` |
| `size of fruits` | `len(fruits)` |
| `fruits with "cherry" added` | `fruits + ["cherry"]` or `fruits.append("cherry")` |
| `let nums be []` | `nums = []` |

Python lists are very similar to E lists. The biggest difference is the
indexing syntax: Python uses **square brackets** `[]` after the list
name. The **last item** is at index `-1`, second-to-last at `-2`, etc.

## Functions (your own commands)

| E | Python |
|---|--------|
| `to square x`<br>`    return x times x`<br>`end` | `def square(x):`<br>`    return x * x` |

Just like with `if`, Python uses a `:` and indentation instead of `end`.
And again, function **calls always have parentheses**, even if there are
no arguments: `say_hello()` not `say_hello`.

## Input from the user

| E | Python |
|---|--------|
| `let name be ask "What's your name? "` | `name = input("What's your name? ")` |

In Python, `input()` always returns a **string**. Even if the user types
`42`, you get back the text `"42"`. To do math with it, convert it:

```python
age_text = input("How old are you? ")
age = int(age_text)        # convert text to integer
```

## Things Python has that E doesn't

1. **Libraries** — Python's superpower. `import math` gives you square
   roots, trigonometry, etc. `import random` gives you dice rolls.
2. **Classes and objects** — a way to bundle data and behavior together.
   You won't need this for a while, but it's how bigger programs are
   organized.
3. **Error handling** — `try: ... except:` lets your program keep
   running even if something goes wrong.
4. **One-liners for lists** — `[x*2 for x in nums]` makes a new list
   where every number is doubled. Very popular in Python.
5. **File I/O** — easy reading and writing of files on disk.

## One thing to watch for

**Python is whitespace-sensitive.** The number of spaces at the start of
a line matters. Use 4 spaces for each level of indentation. Don't mix
tabs and spaces. Most editors handle this for you if you set them up
right (e.g. in VS Code, set "Tab Size" to 4 and "Insert Spaces" on).

If you see a Python error like `IndentationError: unexpected indent`,
that's what it's complaining about.

## Try it

1. Install Python 3 from [python.org](https://python.org).
2. Open a terminal.
3. Type `python` and press Enter. You should see `>>>`.
4. Try your first program:
   ```python
   print("Hello, world!")
   ```
5. Write a file called `hello.py` and run it:
   ```cmd
   python hello.py
   ```
6. When you're ready, walk through the official Python tutorial at
   [docs.python.org/3/tutorial](https://docs.python.org/3/tutorial/).

The thinking is the same. The spelling is different. You'll be fine.
