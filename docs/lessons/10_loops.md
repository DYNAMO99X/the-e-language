# Lesson 10 — Saying it over and over (loops)

**Goal:** Make the computer do the same thing many times without you
having to copy-paste.

**Time:** ~30 minutes.

## Try first (no screen!)

Tell the student: "I want you to say 'hello' 5 times. Go."

Now: "Now I want you to say 'hello' 100 times. Go."

The point: doing it 5 times is fine. Doing it 100 is torture. But
**the program doesn't care** — it will do it 1 time or 1 million times
in the same amount of effort. That's the power of loops.

## Vocabulary

| Word | What it means |
|------|---------------|
| **loop** | A chunk of code that runs again and again. |
| **iterate** | One "round" of the loop. "Loop 10 times" = 10 iterations. |
| **counter** | A number that goes up (or down) each time through the loop. |
| **infinite loop** | A loop that never ends. A bug. |
| **counter variable** | A variable you use to count how many times the loop has run. |

## Demo

Save as `07_loops.e` and run:

```
say "Counting to 10:"
let n be 1
repeat 10 times
    say n
    let n be n plus 1
end
```

You should see the numbers 1, 2, 3, 4, 5, 6, 7, 8, 9, 10.

## Read the code

```
let n be 1
repeat 10 times
    say n
    let n be n plus 1
end
```

- `let n be 1` — start a counter at 1.
- `repeat 10 times` — do the following 10 times.
- `say n` — print the counter.
- `let n be n plus 1` — add 1 to the counter.
- `end` — close the loop.

> **Important:** the line `let n be n plus 1` is the trick. It says
> "take the **old** n, add 1, and store the result back in n." Without
> this, the counter would stay at 1 forever and you'd see "1" 10 times
> in a row.

## Why loops matter

Imagine you wanted to print 1 to 10 WITHOUT a loop. You'd write:

```
say 1
say 2
say 3
...
say 10
```

That's 10 lines. With a loop, it's 4 lines. **For 100 numbers, the
difference is 100 lines vs 4 lines.** For a million, the difference
is a million vs 4.

## Loops with turtle

Loops are how you make cool turtle drawings. A square:

```
let ada be turtle
repeat 4 times
    move ada forward 100
    move ada right 90
end
```

This is the **same as** the 8-line version from Lesson 5, but it's
much shorter and easier to change. Want a 6-sided shape (hexagon)?
Just change the 4 to a 6 and the 90 to a 60:

```
let ada be turtle
repeat 6 times
    move ada forward 100
    move ada right 60
end
```

Want a star? Different angle:

```
let ada be turtle
repeat 5 times
    move ada forward 100
    move ada right 144
end
```

(The math: 360/5 = 72, but to make a star, you turn 180-72 = 144 each
time.)

## The while loop

`repeat N times` is great when you know the number up front. But what
if you don't? What if you want to keep going **until something is
true**? Use `while`.

```
let secret be 7
let guess be 0

while guess is not equal to secret
    let guess be ask "Guess the number (1-10): "
    let guess be number guess
    if guess is less than secret then
        say "Higher!"
    else
        if guess is greater than secret then
            say "Lower!"
        else
            say "You got it!"
        end
    end
end
```

Read it: "while the guess is wrong, keep asking."

> **Warning:** `while` is dangerous. If the condition is **always
> true**, the loop runs forever. Make sure something inside the loop
> changes the condition.

## Tinker

1. Make the loop run 100 times. Try changing `10` to `100`. Run.
2. Print only even numbers (2, 4, 6, 8, ...). Hint: add 2 each time
   instead of 1.
3. Print the 7 times table.
4. Make a triangle: loop 3 times, each time go forward 100 and right
   120.
5. Use `while` to keep asking for a name until the user types
   `"quit"`.

## Break it on purpose

1. Make a counter that never changes: `let n be 1` then `repeat 5
   times` then `say n` then... no `n plus 1`. Run. You see "1" 5
   times. Press Ctrl+C to stop.
2. `while 1 is greater than 0`. That condition is **always** true.
   Run. Watch the computer spew output forever. (Ctrl+C to stop.)
3. Forget `end`. Run. Read the error.

## Common mistakes

- **The loop runs forever** — You forgot the line that changes the
  counter (or changes the `while` condition).
- **The loop runs the wrong number of times** — Off-by-one. If you want
  to count to 10, you start at 1 and stop after 10. If you start at 0
  and stop after 10, that's 11 numbers.
- **`end` missing** — The program doesn't know the loop is over.

## Going further

- **FizzBuzz**: count from 1 to 30. For multiples of 3, print "Fizz".
  For multiples of 5, print "Buzz". For both, print "FizzBuzz". For
  the rest, print the number. (Use `mod` to check.)
- **Drawing a spiral**: start the turtle, and in a loop, go forward
  by 1, 2, 3, 4, ... and turn right 90. Each forward is a bit longer.
- **Guess the number**: use `while` and `random 1, 100` to pick a
  secret number. The user has to guess it. Tell them "higher" or
  "lower" until they get it.

## Exit ticket

Without looking:

1. What's the difference between `repeat 10 times` and `while something is true`?
2. Why does a counter need to "change" inside the loop?
3. Can you draw a 12-sided shape (dodecagon)? What angle do you need?

If yes, on to Lesson 11 — lists!
