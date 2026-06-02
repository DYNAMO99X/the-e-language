# Lesson 2 — Storing things (variables)

**Goal:** Make the program remember things — the user's name, age, or
whatever they type.

**Time:** ~30 minutes.

## Try first (no screen!)

Play a memory game with the student. You say three words. They repeat
them back. Then they go do something else for a minute. Can they still
remember the words? Probably not, unless they wrote them down.

A computer is the same — it forgets things the moment they're not in
use. To remember something, we have to **store** it in a **variable**.

## Vocabulary

| Word | What it means |
|------|---------------|
| **variable** | A named box that holds a value. Like a labeled jar. |
| **assign** | To put a value into a variable. In E: `let x be 5`. |
| **value** | The thing inside the box. Could be a number, a string, or a list. |

## Demo

Type this into `02_variables.e` and run it:

```
let name be ask "What is your name? "
say "Hello, " , name , "!"

let age be ask "How old are you? "
say "You are " , age , " years old."
```

The program will:
1. Pause and ask you to type your name. Press Enter.
2. Print a greeting with your name in it.
3. Pause and ask your age. Press Enter.
4. Print a sentence with your age.

Try running it and typing different answers. The output changes every
time. **That's the magic of variables.**

## Read the code

```
let name be ask "What is your name? "
```

This line does three things:
- `let name be` — create a variable called `name` and put a value in it.
- `ask "What is your name? "` — wait for the user to type something.
  The text in quotes is the **prompt** (the question shown to the user).
- The user's typed answer becomes the **value of `name`**.

After this line, the variable `name` holds whatever the user typed.

```
say "Hello, " , name , "!"
```

The `say` line uses `name`. The comma `,` joins the pieces together.
We'll cover joining in detail in Lesson 3. For now, just notice: we can
**reuse** `name` because we stored it.

## Tinker

1. Add a third question. Ask for the user's favorite color. Then print
   `"Your favorite color is "` followed by their answer.
2. Add a fourth question. Ask for the city they live in.
3. Add an empty line between sections using `say ""`.
4. Change one of the prompts to be friendlier. Use emojis if your
   terminal supports them (most do).

## Break it on purpose

1. Forget the `be` in `let name be ask ...`. What error do you get?
2. Capitalize `let` to `Let`. What happens?
3. Try to `say` a variable that doesn't exist: `say favorite_food`.
   Read the error carefully — E tells you the variable name it didn't
   understand.
4. Use a number in a string: `let favorite_number be 7`. Then
   `say "My favorite number is " , favorite_number`. Notice that
   numbers and strings get joined as text.

## Common mistakes

- **"I don't know what 'ask' means"** — `ask` is a special word, not a
  variable. It only works inside a `let ... be ask ...` line.
- **"I expected a string"** — Inside `say`, every comma-separated piece
  needs to be a value. Did you accidentally type `let` inside a `say`?
- **The program asks but doesn't print** — Did you forget to use a
  `say` line that uses the variable? `let x be ask "..."` only
  stores the value. You have to use it.

## Going further

- Make a "fortune cookie" program. Ask the user three questions, then
  use all three in a single fortune. Example:
  ```
  "You will meet a tall stranger from " , city , " who loves " , color , "."
  ```
- Try a math problem: ask for two numbers and add them. (Hint: you'll
  need `plus`, which we learn in Lesson 4. For now, just store them
  and `say` them back.)

## Exit ticket

Without looking:

1. Can you explain what a variable is in one sentence?
2. Can you write a program that asks the user a question and then
   uses their answer in a `say`?
3. Why does `let x be ask "..."` need both `let` and `be`?

If yes to all three, you're ready for Lesson 3.
