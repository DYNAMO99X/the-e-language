# Lesson 1 — Saying things

**Goal:** Make the computer print whatever you want.

**Time:** ~20 minutes.

## Try first (no screen!)

Before opening the computer, do this with the student:
- Stand up and face a wall.
- Say "Hello" out loud. Then change what you say to "Good morning".
- The wall "ran" your program. The words you said are like the words
  in a `say` statement. Now let's make the computer do the same.

## Vocabulary

| Word | What it means |
|------|---------------|
| **statement** | One instruction the computer will run. |
| **string** | Some text in quotes, like `"hello"`. |
| **print** | Show on the screen. In E, you say it with `say`. |

## Demo

In your text editor, create a new file called `01_say.e` and type this
exactly:

```
say "Hello, world!"
say 'Hi there!'
say `Greetings, traveler.`
```

Save and run it:

```bash
e 01_say.e
```

You should see three lines printed, one after another.

## Read the code

```
say "Hello, world!"
```

- `say` — the verb. Means "print to the screen".
- `"Hello, world!"` — a **string** (a piece of text wrapped in quotes).
- Together: a complete instruction. The computer does it, then moves to
  the next line.

Now look at the other two lines. They look almost the same — but the
**quotes are different**. The first uses `"`, the second uses `'`, the
third uses `` ` `` (the backtick, the key above Tab). All three work
exactly the same way. Pick whichever feels most comfortable.

> **When would I use a different one?** Sometimes your text contains
> one of the quote marks. For example, if you want to say `It's a
> sunny day`, the apostrophe in `It's` would confuse the computer if
> you used single quotes around the whole thing. So you'd write:
> `say "It's a sunny day"`.

## Tinker

Change the program. After each change, run it.

1. Add a fourth `say` line that prints your favorite food.
2. Change `"Hello, world!"` to `Hello, world!` (no quotes). What
   happens? Read the error message.
3. Use the backtick `` ` `` for one of your lines. (It's the key
   above Tab, usually.)
4. Make a multi-line poem. At least 4 lines.

## Break it on purpose

Try these **on purpose** to see what E's error messages look like:

1. Forget the closing quote: `say "Hello`. Run it. What does E say?
2. Capitalize `say` to `Say`. Run it. What does E say?
3. Add a word that isn't a string and isn't `say`: `say hello`. What
   does E say?

These errors are your friends. They tell you what's wrong. E is much
friendlier than most languages about this.

## Common mistakes

- **"I expected a string"** — You forgot quotes around your text.
  Remember: text is always inside quotes.
- **"I started reading a string but never found the closing quote"** —
  You have a quote but no matching close. Check for `"` and make sure
  each one has a partner.
- **The program runs but nothing prints** — You might have written
  `Say` with a capital S. E is case-sensitive for some things.

## Going further

- Can you make a program that prints a smiley face using only letters,
  dashes, and pipes? Like `:-)` or `(-_-)` or `(>_<)`.
- Try printing something with a backslash in it. (Hint: you'll need
  `\\` to actually print a single backslash. Why?)

## Exit ticket

Without looking at the lesson:

1. Write a program that prints three different lines.
2. Use a `say` statement with a `'` quote and one with a `` ` `` quote.
3. Explain to someone why strings need quotes around them.

If you can do all three, you understand Lesson 1. On to Lesson 2!
