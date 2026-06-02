# Lesson 10 — Functions calling themselves (recursion)

**Goal:** Have a function call itself to solve a smaller version of
the same problem.

**Time:** ~30 minutes.

> **This is the hardest lesson so far.** Take your time. If you get
> lost, that's normal. Come back to it.

## Try first (no screen!)

This is a famous riddle. Read it slowly.

> A farmer is trying to get a fox, a chicken, and a bag of grain
> across a river. The boat can only hold the farmer and **one** of
> the three things. If the farmer leaves the fox alone with the
> chicken, the fox eats the chicken. If the farmer leaves the chicken
> alone with the grain, the chicken eats the grain. How does the
> farmer get everything across?

The trick: each step is a smaller version of the same problem.
"That's a recursion." — Well, almost. It's actually a recursion
**with state** because the farmer's location matters. But the
**shape** is the same: do a small piece, then solve the rest.

## Vocabulary

| Word | What it means |
|------|---------------|
| **recursion** | A function that calls itself. |
| **base case** | The "stop" — when the function doesn't call itself anymore. |
| **recursive case** | When the function calls itself with a smaller input. |
| **infinite recursion** | When the function calls itself forever. The program crashes. |

## Demo

Save as `10_recursion.e` and run:

```
to factorial n
    if n is less than or equal to 1 then
        return 1
    end
    return n times (factorial (n minus 1))
end

let f5 be factorial 5
say "5! = " , f5
```

Output: `5! = 120`

## What is factorial?

`5!` (read "5 factorial") is:
```
5 × 4 × 3 × 2 × 1 = 120
```

It's used a lot in math. The trick: 5! = 5 × 4!. And 4! = 4 × 3!.
And so on. So:

```
factorial(n) = n × factorial(n-1)
```

That's recursion! The function is defined **in terms of itself**, with
a smaller `n`.

## Read the code

```
to factorial n
    if n is less than or equal to 1 then
        return 1
    end
    return n times (factorial (n minus 1))
end
```

Two parts:

**Base case:** `if n is less than or equal to 1 then return 1`.

When `n` is 1 (or less), the function stops calling itself and just
returns 1. **Every recursive function needs a base case.** Without
it, the function calls itself forever and the program crashes.

**Recursive case:** `return n times (factorial (n minus 1))`.

The function calls itself with a **smaller** argument: `n minus 1`.
Then it multiplies the result by `n` and returns that.

> **Note:** When calling a function inside an expression, wrap it in
> parentheses. `n times factorial(n minus 1)` would work too — the
> parens are a habit that keeps things clear.

## Step through it

Let's say we call `factorial 3`. Here's what happens:

```
factorial(3)
  return 3 × factorial(2)
            factorial(2)
              return 2 × factorial(1)
                        factorial(1)
                          return 1  <-- base case hit!
              return 2 × 1 = 2
  return 3 × 2 = 6
```

So `factorial 3` returns 6. And `3!` is `3 × 2 × 1 = 6`. ✓

## Why is this useful?

Some problems are **naturally recursive**. A tree (folder structure):
each folder has files and other folders. Each of those folders has
files and other folders. To list everything, you list a folder, then
list each of its subfolders the same way. Recursion!

Trees, hierarchies, searching, sorting — they all use recursion.

## Tinker

1. Compute factorials from 1 to 10. (`factorial 1` = 1, `factorial 2`
   = 2, `factorial 3` = 6, `factorial 4` = 24, ...)
2. Write `sum_to n` that returns the sum 0 + 1 + ... + n. Use
   recursion.
3. Write `fibonacci n` that returns the n-th Fibonacci number:
   `fib(0) = 0`, `fib(1) = 1`, `fib(n) = fib(n-1) + fib(n-2)`. So
   `fib(5) = 5`.
4. Write `countdown n` that prints n, n-1, ..., 1 using recursion.

## Break it on purpose

1. Forget the base case. Run. What happens? (Probably "the program ran
   forever and then the stack overflowed".)
2. Use the same `n`: `return n times (factorial n)`. The
   argument never gets smaller, so it's infinite recursion.
3. Off-by-one in the base case. `if n is less than 0 then return 1`.
   Try `factorial 0`. It'll loop forever.

## Common mistakes

- **Stack overflow / infinite recursion** — The base case is wrong,
  or the recursive call uses the same value.
- **Returns the wrong answer** — Maybe you used `+` instead of `times`.
  Or the base case returns 0 instead of 1.
- **"I expected a value but got nothing"** — You forgot the `return`
  in the base case. The function ran but had no result.

## Going further

### Trees with turtle (preview of Lesson 11!)

```
to tree depth length
    if depth is 0 then
        return
    end
    move ada forward length
    move ada left 30
    tree (depth minus 1), (length times 0.7)
    move ada right 60
    tree (depth minus 1), (length times 0.7)
    move ada left 30
    move ada backward length
end

let ada be turtle
move ada left 90
tree 6, 100
```

You don't need to fully understand this yet. Save it for Lesson 11
where we'll walk through how the recursion makes the picture.

## Exit ticket

Without looking:

1. What's a base case?
2. Why does the recursive call need to use a **smaller** input?
3. What would happen if the base case was wrong?
4. Can you write `sum_to n` from scratch? (No peeking.)

If you got the last one, you're in great shape for Lesson 11 — using
recursion to draw pictures!
