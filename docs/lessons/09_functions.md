# Lesson 9 — Your own commands (functions)

**Goal:** Group code into reusable chunks that you can call by name.

**Time:** ~30 minutes.

## Try first (no screen!)

Pick a 3-step action the student does a lot, like getting ready for
school: (1) put on shoes, (2) grab backpack, (3) walk to the door.

Ask: "What's that called?" — Getting ready.

"Now if I say 'get ready', you do all three steps, right?" — Yes.

"That's a function. **Get ready** is the name. It runs the three steps
in order, every time. You can call it whenever, as many times as you
want."

## Vocabulary

| Word | What it means |
|------|---------------|
| **function** | A named chunk of code that does something. |
| **define** | To write a function. The function exists, but hasn't run yet. |
| **call** | To run a function. The function actually does its thing. |
| **parameter** | A placeholder value you give to a function. |
| **argument** | The actual value you pass in. |
| **return** | To give back a value. |
| **call stack** | A list of function calls that are in progress. |

## Demo

Save as `09_functions.e` and run:

```
to greet name
    say "Hello, " , name , "!"
end

greet "Alice"
greet "Bob"
greet "Charlie"
```

Output:
```
Hello, Alice!
Hello, Bob!
Hello, Charlie!
```

## Read the code

```
to greet name
    say "Hello, " , name , "!"
end
```

This is a **function definition**. It says: "I'm defining a function
called `greet`. It takes one parameter, called `name`. Inside the
function, do this."

```
greet "Alice"
```

This is a **function call**. It says: "Run the function `greet`, and
pass in `"Alice"` as the value of `name`."

So when `greet` runs, the variable `name` (inside the function) is set
to `"Alice"`. Then `say "Hello, " , name , "!"` becomes `say "Hello,
Alice!"`. The function ends. Back in the main program, the next
line runs.

## Functions that return values

Sometimes you want a function to **give you an answer** instead of
printing. Use `return`.

```
to square n
    let result be n times n
    return result
end

let x be square 5
say "5 squared is " , x
```

Here, `square 5` runs: it computes 25 and **returns** 25. The return
value goes wherever the call was. Since it's on the right side of
`let x be`, the value 25 is stored in `x`.

> **Important:** When a function hits `return`, it stops running
> immediately, even if there are more lines after it. Use this to
> bail out early.

## Multiple parameters

Functions can take more than one parameter. You separate the values
with **commas** when you call the function.

```
to add a b
    return a plus b
end

let sum be add 3, 4
say "3 + 4 = " , sum
```

Inside the function, the parameters are just a list of names — no
commas. `to add a b` not `to add a, b`.

> **Note:** If you have more than one argument, you must separate
> them with commas. `add 3 4` won't work; use `add 3, 4`. The comma
> tells E "this is a new argument."

For complex arguments, wrap them in parens:

```
to triple x
    return x times 3
end

let result be triple (5 plus 2)
say result          -- 21
```

The `(5 plus 2)` makes sure E evaluates the whole expression before
passing it to `triple`.

## Tinker

1. Write a function `double x` that returns `x times 2`.
2. Write a function `bigger a, b` that returns whichever of `a` or
   `b` is larger.
3. Write a function `say_twice text` that says `text` twice.
4. Combine with a loop: have a function `draw_square` that draws a
   100x100 square. Call it 5 times with the turtle.

## Break it on purpose

1. Forget `end`: remove the `end` after a function. Run. What error?
2. Use the function before defining it: call a function that's below.
   What error? (E reads top to bottom, so functions must be defined
   **before** they're called. If you need to call them out of order,
   you need to know about... uh, "forward declarations". E doesn't
   have those yet. Just keep the order.)
3. Forget to capture the return: `square 5` alone, without
   `let x be`. The function runs and computes 25, but the result is
   thrown away.
4. Use the wrong number of args: `greet` (no name). What error?

## Common mistakes

- **"I don't know a command called 'greet'"** — Either you haven't
  defined it yet, or you have a typo.
- **The function runs but the result is wrong** — Maybe you forgot
  `return` and just used `say`. `say` prints, but the function's value
  is `nothing` (in E, the keyword is implicit — if you never return,
  the function has no result).
- **"expects 2 arguments but I got 1"** — You forgot the comma
  between arguments. `add 3 4` should be `add 3, 4`.
- **The function name is being treated as text** — Make sure you wrote
  `greet "Alice"`, not `say greet`.

## Going further

### Refactor the tip calculator

Take the Lesson 4 tip calculator and wrap it in a function:

```
to tip_calculator
    let bill be ask "How much was the bill? "
    let bill_num be number bill
    let tip be bill_num times 15 divided by 100
    let total be bill_num plus tip
    say "Tip: " , tip
    say "Total: " , total
end

tip_calculator
tip_calculator
```

Now the same calculator runs twice in a row. Functions let you **do
the same thing many times with less code**.

### The square of all the things

```
to print_squares count
    let i be 0
    repeat count times
        say i , " squared is " , (i times i)
        let i be i plus 1
    end
end

print_squares 10
```

## Exit ticket

Without looking:

1. What's the difference between **defining** and **calling** a
   function?
2. What's the difference between a **parameter** and an **argument**?
3. How do you get a value back from a function?
4. Why are functions useful? (More than one reason is OK.)

If yes, on to Lesson 10 — functions calling themselves (recursion)!
