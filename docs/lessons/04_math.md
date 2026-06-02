# Lesson 4 — Doing math

**Goal:** Make the computer do arithmetic for you.

**Time:** ~30 minutes.

## Try first (no screen!)

Ask the student: "If a pizza costs $18 and you want to leave a 15% tip,
how much is the tip? How much is the total?"

Let them try to figure it out on paper. The math is:
- 15% of 18 = 18 × 0.15 = 2.70
- Total = 18 + 2.70 = 20.70

Now show them how the computer does the same thing — instantly, no
mistakes, every time. **That's the point of math in programs.** A
computer is a really fast, really cheap calculator that can also do
other things.

## Vocabulary

| Word | What it means |
|------|---------------|
| **operator** | A symbol or word that does math. `+`, `-`, `×`, etc. |
| **operand** | The thing you're doing math on. `3 + 4`: 3 and 4 are operands, `+` is the operator. |
| **precedence** | The order operations happen in. Multiplication before addition. |
| **integer** | A whole number, like 5 or -12. No decimal point. |
| **float** | A number with a decimal point, like 3.14. |

## Demo

Type this into `04_math.e` and run it. Try with different bill amounts.

```
say "Tip calculator!"
say ""

let bill be ask "How much was the bill? "
let bill_num be number bill

let tip be bill_num times 15 divided by 100
let total be bill_num plus tip

say "15% tip is " , tip
say "Total: " , total
say ""

let half be bill_num divided by 2
say "Split with one friend: " , half , " each"
```

When asked for the bill, type something like `20` or `42.50`.

## Read the code

```
let bill be ask "How much was the bill? "
let bill_num be number bill
```

Why two lines? Because `ask` always returns **text** (the user might
type anything). To do math, we need a **number**. The `number` function
converts text to a number. If the user types `20`, `bill_num` is the
**integer** 20. If they type `abc`, the program will stop and say
"I can't turn the text 'abc' into a number."

```
let tip be bill_num times 15 divided by 100
```

E reads this left to right:
- `bill_num times 15` → if `bill_num` is 20, this is 300.
- `300 divided by 100` → 3.0 (a float, because division in E is
  always float).
- So `tip` is `3.0`.

> **Order of operations:** E evaluates left to right, one operator at
> a time. There's no "multiplication before division" rule — the
> operations happen in the order you write them. If you want to be
> sure, use parentheses: `(bill_num times 15) divided by 100`.

## The math operators

| E | Math | Example |
|---|------|---------|
| `plus` | + | `5 plus 3` → 8 |
| `minus` | - | `10 minus 4` → 6 |
| `times` | × | `6 times 7` → 42 |
| `divided by` | ÷ | `10 divided by 3` → 3.333... |
| `mod` | remainder | `10 mod 3` → 1 |

`mod` is a special one. `10 mod 3` is "what's left over when you
divide 10 by 3?" Answer: 1. It's super useful for telling if a number
is even or odd: `x mod 2` is 0 if `x` is even, 1 if `x` is odd.

## Tinker

1. Change the tip to 20%. (Hint: `bill_num times 20 divided by 100`.)
2. Add a line that calculates the tax: 8% of the bill. Add it to the
   total.
3. Make a "split among N friends" calculator. Ask how many friends.
4. Try `let weird be 10 mod 3` and `say weird`. What does it print?
5. Try `let answer be 5 plus 5 times 2`. Is it 15 (math class order)
   or 20 (left to right)?

## Break it on purpose

1. Divide by zero: `let x be 10 divided by 0`. Read the error.
2. Try to do math on text: `let x be "hello" plus "world"`. What
   happens? (`plus` does math, not text — use `,` for that.)
3. Forget a number: `let x be 5 plus`. E will tell you it expected
   another number.

## Common mistakes

- **"I can't turn the text into a number"** — The user typed something
  that's not a number. Or you forgot the `number` call.
- **The math gives the wrong answer** — Order of operations. Wrap in
  parens to be safe.
- **`times` is being used for "hours" or something** — `times` is
  multiplication only. In a sentence, use a different word.

## Going further

- Make a temperature converter: F to C. Formula: `C = (F - 32) times 5 divided by 9`.
- Make a coin-counting program: ask for the number of quarters, dimes,
  nickels, and pennies. Multiply and add them up.
- Make a "how old are you in days" program: `age times 365`.

## Exit ticket

Without looking:

1. What's the difference between `5 divided by 2` and `5 mod 2`?
2. Can you calculate 20% of 85 in a single line of E code?
3. Why do we need `number` after `ask`?

If yes to all three, you're ready for Lesson 5 — your first turtle!
