# Lesson 14 — Reading errors and debugging

**Goal:** Get good at fixing broken programs. Every programmer does
this all day long.

**Time:** ~30 minutes.

> **The most important lesson in this curriculum.** You will spend
> more time debugging than writing. Get good at it.

## What is "debugging"?

A "bug" is a mistake in your program. "Debugging" is finding and
fixing it. Old story: in 1947, a moth got stuck in a Harvard
computer. They "debugged" it by removing the moth. The word stuck.

Every programmer — even the best — spends most of their time
debugging. It's not a sign you're bad. It's a sign you're doing the
work.

## The most common kinds of errors

### 1. Syntax errors — "I don't understand what you wrote"

E tells you the line and what's wrong. Read it!

```
say "hello
```

E says: *I expected the end of a string but I hit the end of the
line. (Did you forget a closing quote?)*

Fix: add the closing quote.

### 2. Name errors — "I don't know what 'X' is"

```
let x be 5
say y
```

E says: *I don't know a variable called 'y'. Did you mean 'x'?*

Fix: typo. Or you forgot to define `y` first.

### 3. Type errors — "I can't do that with these values"

```
let x be "hello" plus 5
```

E says: *I can't do plus with text and a number. Maybe you meant to
use , (comma) to join them as text?*

Fix: do the conversion first. `number` to make 5 → 5, or
concatenate with `,`.

### 4. Logic errors — "It runs but the answer is wrong"

E doesn't catch these. The program runs, gives you the wrong
answer, and you have to figure out why.

```
let score be 90
if score is greater than 100 then
    say "You got a bonus"
end
```

A score of 90 is not greater than 100, so the message doesn't print.
But the program doesn't complain. **The bug is in your thinking,
not in the code.**

## The debugging method

When your program doesn't work, **don't panic, don't guess**. Go
through these steps in order:

### Step 1: Read the error message

E tries to be helpful. The error tells you:
- **What** went wrong (in English)
- **Where** (line number)
- **Sometimes:** what to try instead

Read it out loud. Twice.

### Step 2: Look at the line E complains about

E gives you a line number. Go there. The bug is usually **on that
line** or **the line above it**.

### Step 3: Check your spelling

E is case-sensitive. `name` and `Name` are different. `Say` and `say`
are different. Most errors are typos.

### Step 4: Print to figure out what's happening

If the answer is wrong but no error fires, you need to see the
values. Add `say` lines to print things out:

```
let x be ask "Type a number: "
let x_num be number x
say "DEBUG: x_num is " , x_num

let y be x_num plus 10
say "DEBUG: y is " , y

say "Final: " , y
```

Run it. The DEBUG lines show you the values at each step. The bug
becomes obvious.

### Step 5: Walk through the code by hand

Pretend you're the computer. Take a pen and paper. Write down each
variable as it changes. Compare with what you expected.

This is **incredibly effective** and feels old-fashioned. It works
because programs run in order, and so does your paper.

### Step 6: Make a smaller version

If a 200-line program is broken, **delete half of it**. Does the
remaining half work? Add the other half back in pieces. Find the
piece that broke.

## Common error patterns in E

| Error | Likely cause | Fix |
|-------|-------------|-----|
| I expected end of input | You forgot `end` somewhere. | Count your `if`, `repeat`, `while`, `to`. They should each have an `end`. |
| I don't know a command called... | Typo, or function defined later. | Check spelling. Make sure `to greet` is **above** the call to `greet`. |
| I expected a number | Math on text, or missing argument. | Use `number` to convert. Or fill in the argument. |
| I expected end of string | Missing closing quote. | Find the string and add `"` (or `'` or `` ` ``). |
| I can't do X with these | Wrong types. | Number for math, text for `,`. |
| I tried to get item N from a list of size M | List index out of range. | Valid indices are 0 to M-1. |
| The stack overflowed | Recursive function with no base case. | Add a base case that returns without calling itself. |

## Tinker with broken programs

Below are some broken programs. **Find the bug and fix it.** The
answer is in the section after each one, but don't peek.

### Bug 1: The greeter

```
to greet name
    say "Hello, " , nam
end

greet "Alice"
```

<details>
<summary>Hint</summary>

The error is on the `say` line. Look at the variable name.
</details>

<details>
<summary>Answer</summary>

`nam` should be `name`. Typo. The function expects `name` because
that's what the parameter says, but inside the function we wrote
`nam`. So `nam` doesn't exist.
</details>

### Bug 2: The counter

```
let n be 1
repeat 10 times
    say n
    n plus 1
end
```

<details>
<summary>Answer</summary>

`n plus 1` doesn't do anything. It computes the value but doesn't
store it. It should be `let n be n plus 1`. (This was Lesson 8's
gotcha.)
</details>

### Bug 3: The list lookup

```
let pets be [ "dog" , "cat" , "fish" ]
say pets at 0
say pets at 1
say pets at 2
```

This actually runs! The bug is more subtle: the user **expected**
to get the dog first, but if you change the order in the list
it works fine. Wait — there's no bug here. Try this instead:

```
let pets be [ "dog" , "cat" , "fish" ]
say pets at 3
```

<details>
<summary>Answer</summary>

The list has 3 items, valid indices are 0, 1, 2. `pets at 3` is out
of range. E will tell you the valid range in the error message.
</details>

### Bug 4: The infinite loop

```
let n be 1
while n is less than 10
    say n
end
```

<details>
<summary>Answer</summary>

`n` never changes, so the condition is always true. The loop runs
forever. Either add `let n be n plus 1` inside the loop, or change
the condition so it can become false. (Ctrl+C to stop the runaway
program.)
</details>

### Bug 5: The wrong answer

```
to area width, height
    return width plus height
end

say "10 by 5 area: " , (area 10, 5)
```

<details>
<summary>Answer</summary>

The output is 15. The area of a 10 by 5 rectangle is 50, not 15.
The function is using `plus` instead of `times`. Should be
`width times height`.
</details>

## Going further

- Try the **rubber-duck debugging** method. Get a rubber duck (or any
  object). Explain your program to the duck, line by line. Most of
  the time, the bug becomes obvious while you're explaining.
- Make a "bug journal". Every time you fix a bug, write down:
  - What the program was supposed to do
  - What it did instead
  - The line that was wrong
  - What the fix was

  After a few weeks, you'll see patterns. You'll stop making the
  same mistakes.

- Learn to **read other people's programs**. Find a friend's .e
  file (or write one, then ask the student to find the bug).
  Reading unfamiliar code is a great skill.

## Exit ticket

Without looking:

1. What's the difference between a syntax error and a logic error?
2. What's the first thing you should do when you see an error?
3. Why are `say` lines useful for debugging?

If yes, on to Lesson 15 — planning a small project!
