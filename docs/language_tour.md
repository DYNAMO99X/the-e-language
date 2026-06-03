# E — A Friendly Tour of the Language

Welcome to E! E is a tiny programming language designed to read like plain
English. This tour will show you everything you need to know, one concept
at a time.

## Your first program

Create a file called `hello.e`:

```e
say "Hello, world!"
```

Run it with `python e.py hello.e`. You should see `Hello, world!` printed.

## Saying things

`say` prints things to the screen.

```e
say "Hello"
say 42
say true
```

E also accepts `'` and `` ` `` as string delimiters — pick whichever is most
comfortable. They are 100% equivalent and support the same escape sequences
(`\n`, `\t`, `\\`, `\"`, `\'`, `` \` ``).

```e
say 'Hello'
say `Hello`
say 'Don\'t worry'    -- "Don't worry"
```

### Joining things with `,`

Use a comma (`,`) to glue multiple things together into one message:

```e
say "Hello, " , "world"          -- "Hello, world"
say "I am " , 25 , " years old"  -- "I am 25 years old"
```

The comma turns each piece into text and sticks them together.

## Comments

Anything after `--` on a line is a comment and is ignored.

```e
-- this is a comment
say "hi"  -- this is also a comment
```

## Variables

Use `let` to give a name to a value.

```e
let name be "Alice"
let age be 30
let happy be true
```

You can change a variable's value by re-using `let` with the same name:

```e
let score be 0
let score be 10   -- score is now 10
```

## Numbers and math

E knows the usual math operations — spelled out in English or as symbols:

```e
say 3 plus 4           -- 7       (or: 3 + 4)
say 10 minus 3         -- 7       (or: 10 - 3)
say 5 times 3          -- 15      (or: 5 * 3)
say 10 divided by 4    -- 2.5     (or: 10 / 4)
say 10 mod 3           -- 1 (remainder)
```

Use parentheses to control the order:

```e
say 2 plus 3 times 4      -- 14  (3*4 first)
say (2 plus 3) times 4    -- 20  (2+3 first)
```

Negative numbers work too:

```e
say -5
let temp be -10
```

## Asking for input

Use `ask` to read a line of text from the user. The result is always text:

```e
let name be ask "What is your name? "
say "Hello, " , name
```

If you need a number, wrap `ask` in `number(...)`:

```e
let age be number(ask "How old are you? ")
```

## Comparisons

You can compare values with friendly English words or standard symbols:

| Expression                    | Symbol | Meaning          |
|------------------------------|--------|------------------|
| `x is 5`                     | `x = 5` or `x == 5` | equal       |
| `x is equal to 5`            | —      | equal (verbose)  |
| `x is not equal to 5`        | `x != 5` | not equal      |
| `x is greater than 5`        | `x > 5` | >                |
| `x is less than 5`           | `x < 5` | <                |
| `x is greater than or equal to 5` | `x >= 5` | >=          |
| `x is less than or equal to 5`    | `x <= 5` | <=          |

You can mix English and symbols freely:

```e
let age be 25

-- all of these are equivalent:
if age > 18 then say "adult" end
if age is greater than 18 then say "adult" end
if age >= 18 then say "adult" end
if age is greater than or equal to 18 then say "adult" end
```

```e
if age is greater than 18 then
    say "You are an adult"
end
```

## True/False logic

```e
say true and false       -- false
say true or false        -- true
say not true             -- false
```

Truthiness: only `false` and `nothing` are "falsy". Everything else is "truthy".

## Making choices: `if` / `else`

```e
if score is greater than 90 then
    say "Excellent!"
else if score is greater than 70 then
    say "Good job"
else
    say "Keep trying"
end
```

The chain can be as long as you like. Just one `end` at the bottom.

## Repeating things

### Repeat N times

```e
repeat 3 times
    say "hello"
end
```

### While something is true

```e
let n be 0
while n is less than 5
    say n
    let n be n plus 1
end
```

### For each item in a list

```e
let fruits be ["apple", "banana", "cherry"]
for each fruit in fruits
    say fruit
end
```

## Lists

A list is a collection of values in square brackets.

```e
let nums be [1, 2, 3, 4, 5]
let words be ["hello", "world"]
let mixed be [1, "two", true]   -- lists can hold any types
```

Get an item by its position (starting at 0):

```e
say nums at 0       -- 1
say nums at 2       -- 3
```

Get the number of items:

```e
say size of nums    -- 5
```

Add an item:

```e
let nums be nums with 6 added
say nums            -- [1, 2, 3, 4, 5, 6]
```

## Functions

Define a function with `to`. End it with `end`.

```e
to greet name
    say "Hello, " , name
end

greet "Alice"
greet "Bob"
```

Functions can return values:

```e
to square x
    return x times x
end

let result be square 5
say result          -- 25
```

Functions can take more than one argument (separate them with commas):

```e
to add a b
    return a plus b
end

say add 3, 4        -- 7
```

Use parentheses when you need to pass a complex expression:

```e
say add (10 minus 3), (2 times 2)   -- 9
```

Functions can call themselves (recursion):

```e
to factorial n
    if n is less than 2 then
        return 1
    end
    return n times factorial(n minus 1)
end

say factorial 5     -- 120
```

## Built-in functions

E comes with a few helpers:

| Function       | What it does                              |
|----------------|-------------------------------------------|
| `ask`          | Read a line of text from the user         |
| `number(x)`    | Convert a value to a number               |
| `text(x)`      | Convert a value to text                   |
| `uppercase(s)` | Turn text into UPPERCASE                  |
| `lowercase(s)` | Turn text into lowercase                  |
| `random(a, b)` | A random number between a and b           |

## Drawing with the turtle

E comes with a built-in turtle that draws on a canvas — perfect for
visual feedback while learning. To use it, you first *create* a turtle
and give it a name:

```e
let ada be turtle
```

`ada` is now a turtle sitting at the center of the canvas, facing right.

### Moving and turning

```e
move ada forward 100      -- walk 100 pixels
move ada backward 50      -- walk 50 pixels the other way
move ada right 90         -- turn 90° right (clockwise)
move ada left 45          -- turn 45° left
```

### The pen (drawing or not)

By default, the pen is down (the turtle draws as it moves).

```e
make ada close pen        -- pen up: walk without drawing
make ada open pen         -- pen down: draw as you walk
```

### Cursor

```e
make ada hide             -- hide the arrow
make ada show             -- show the arrow
```

### Erasing and resetting

```e
make ada erase all        -- clear the drawing (keep the turtle where it is)
make ada go home          -- move the turtle back to (0, 0), facing right
make ada restart          -- factory reset: erase + home + reset all settings
```

### Drawing shapes

```e
make ada draw circle 50   -- draw a circle of radius 50
make ada draw dot 5       -- draw a filled dot of size 5
```

### Jumping to a position

There are two ways:

```e
-- Relative (using English directions):
make ada goto 50 right and 20 up      -- moves to (current_x + 50, current_y + 20)

-- Raw (absolute coordinates):
make ada go to 100 and 50             -- jumps to exactly (100, 50)
```

The four direction words are: `right` (positive x), `left` (negative x),
`up` (positive y), `down` (negative y).

### Styling

```e
set ada pen color to "red"             -- any color name
set ada pen size to 5                  -- line thickness
set ada background to "white"          -- canvas color
```

### Speed

```e
make ada speed 0                      -- 0 = instant, no animation
make ada speed 5                      -- 1-10, slow to medium
make ada speed 10                     -- fastest animated speed
```

### Reading values from the turtle

```e
let h be ada heading      -- current direction in degrees
let x be ada x            -- current x position
let y be ada y            -- current y position

say "ada is at (" , x , ", " , y , ") facing " , h , " degrees"
```

### Putting it together — a square

```e
let ada be turtle
move ada forward 100
move ada right 90
move ada forward 100
move ada right 90
move ada forward 100
move ada right 90
move ada forward 100
```

### Multiple turtles

You can have more than one turtle, each with its own name:

```e
let ada be turtle
let bob be turtle

move ada forward 50
move bob right 90
move bob forward 50
```

### Headless / text mode

If there's no display available (or you want to log commands to the
console instead of opening a window), use the `--turtle-mode text` flag:

```cmd
e --turtle-mode text my_drawing.e
```

In text mode, every command is printed to the console so you can see
what your program *would have* drawn without needing a window. Useful
for learning, debugging, or running on a server.

## Special values

| Value     | What it is                  |
|-----------|----------------------------|
| `true`    | The true boolean           |
| `false`   | The false boolean          |
| `nothing` | The "no value" value (like null) |

## Interactive mode (the REPL)

Run `python e.py` with no file to enter interactive mode:

```
$ python e.py
Hi! Ready to code?
> let x be 5
> say x
5
> let y be x plus 1
> say y
6
> bye
E: bye!
```

Type `bye`, `exit`, or `quit` to leave.

## Putting it all together

Here's a small program that uses almost everything:

```e
to fib n
    if n is less than 2 then
        return n
    end
    return fib(n minus 1) plus fib(n minus 2)
end

let count be number(ask "How many fib numbers? ")

let results be []
let i be 0
while i is less than count
    let results be results with fib i added
    let i be i plus 1
end

say "Here are " , count , " fibonacci numbers:"
for each num in results
    say num
end
```

Have fun!
