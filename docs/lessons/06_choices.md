# Lesson 6 — Making choices (if / else)

**Goal:** Make the program do different things based on what the user
types or what the math says.

**Time:** ~30 minutes.

## Try first (no screen!)

Tell the student: "I'm going to say a number. If the number is bigger
than 50, you say 'big'. If it's smaller, you say 'small'. If it's
exactly 50, you say 'fifty'."

Throw numbers at them: 30, 75, 50, 10, 99. They have to decide each
time. **This is what `if` does in a program** — the computer makes a
decision, and the program does different things based on it.

## Vocabulary

| Word | What it means |
|------|---------------|
| **condition** | A question with a yes/no answer. In E: `x is greater than 5`. |
| **branch** | One of the paths the program might take. |
| **comparison** | Comparing two values: `5 is greater than 3` is true. |
| **boolean** | A value that's either `true` or `false`. |

## Demo

Save as `06_choices.e` and run. Try different ages and scores.

```
let age be ask "How old are you? "
let age_num be number age

if age_num is greater than or equal to 18 then
    say "You are an adult."
else
    say "You are a kid."
end
```

## Read the code

```
if age_num is greater than or equal to 18 then
    say "You are an adult."
else
    say "You are a kid."
end
```

Let's break it down:
- `if age_num is greater than or equal to 18 then` — the question. If
  the answer is true, do the next part. `then` marks the end of the
  question. (You can leave it off and start a new line instead.)
- `say "You are an adult."` — what happens if the answer was true.
- `else` — what to do if the answer was false.
- `say "You are a kid."` — what happens if the answer was false.
- `end` — closes the `if`. Don't forget this!

> **Note on indentation:** the lines inside the `if` and `else` are
> indented with 4 spaces. This isn't required in E (unlike Python),
> but it makes the code much easier to read. Get into the habit.

## The comparison operators

| E | What it means |
|---|---------------|
| `is equal to` | Are they the same? |
| `is not equal to` | Are they different? |
| `is greater than` | Is the left bigger? |
| `is less than` | Is the left smaller? |
| `is greater than or equal to` | Bigger or the same? |
| `is less than or equal to` | Smaller or the same? |

The **multi-word** ones are important. E matches the longest one
first. So `is greater than or equal to` is recognized as one phrase,
not three separate words.

## Chained conditions (else if)

You can chain multiple checks together. The second example in the demo
file is a grade calculator:

```
if score_num is greater than 90 then
    say "Grade: A"
else
    if score_num is greater than 80 then
        say "Grade: B"
    else
        if score_num is greater than 70 then
            say "Grade: C"
        else
            say "Grade: F"
        end
    end
end
```

This is harder to read because of all the nested `end`s. There's
a cleaner way coming in Lesson 7 once we know about loops. For now,
**nesting is fine** — just count your `end`s and make sure they match.

## Tinker

1. Add a new condition: if `age_num is equal to 13`, say "teenager".
2. Change the grade boundaries. Use the standard: 90+ A, 80+ B, 70+ C,
   60+ D, else F. (Need to add the D branch.)
3. Add a check for negative ages: if `age_num is less than 0`, say
   "you can't be negative years old!"
4. Use `is not equal to` somewhere. Try checking if the user's name
   is not "quit".

## Break it on purpose

1. Forget the `end`: remove the last line. Run. What error?
2. Use `=` instead of `is equal to`: `if age_num = 18`. Read the error.
   (E doesn't use `=` for equality; that's Python's job.)
3. Compare with a string: `if name is greater than 5`. What error?
4. Forget `then`: `if age_num is greater than 18`. Run. (It might
   actually work in E because `then` is optional. Try both ways!)

## Common mistakes

- **"I expected 'end' but I found 'say'"** — You forgot to close an
  `if` with `end`. Count your `if`s and `end`s — they should match.
- **The wrong branch always runs** — Your condition is the opposite
  of what you think. Try inverting `is greater than` to `is less than`.
- **Strings being compared with `>`** — That doesn't work in E. If
  you need to sort strings, you'd need to ask the user for a number
  instead.

## Going further

- Make a "pass / fail" program. Ask for a score. If 60 or more, pass.
  If less, fail.
- Make a "movie rating" program. Ask the user's age. Based on it, tell
  them which movies they can watch: G, PG, PG-13, R.
- Make a "rock paper scissors" program. Ask the user for their choice.
  Pick a random one for the computer using `random 1, 3` (1=rock,
  2=paper, 3=scissors). Compare.

## Exit ticket

Without looking:

1. Can you write an `if` that checks if a number is between 1 and 10?
2. What's the difference between `=` and `is equal to` in E?
3. Why does every `if` need an `end`?

If yes, on to Lesson 7 — loops!
