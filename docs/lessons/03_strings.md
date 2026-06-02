# Lesson 3 — Joining words (the comma trick)

**Goal:** Build sentences by stitching pieces of text together.

**Time:** ~25 minutes.

## Try first (no screen!)

Tell the student: "I'm going to give you four words, and you have to
build a sentence. The words are: **cat**, **sits**, **on**, **mat**."

Then say: "Now build a sentence using the comma trick: cat , sits ,
on , mat. What do you get?"

The student should figure out: it's "catsitsonmat". (No spaces, because
we didn't say where the spaces go!)

**The lesson**: in real programs, you have to put the spaces where you
want them. The comma just glues; it doesn't add anything.

## Vocabulary

| Word | What it means |
|------|---------------|
| **concatenate** | A fancy word for "stick strings together". The comma `,` does this. |
| **glue** | The thing in the middle. In E it's `,`. In Python it's `+`. |
| **whitespace** | Spaces, tabs, and newlines. The stuff that's invisible. |

## Demo

Type this into `03_strings.e` and run it:

```
let name be ask "What is your name? "
let color be ask "What's your favorite color? "
let animal be ask "What's your favorite animal? "

say "Once upon a time, " , name , " went on a quest."
say "Along the way, they met a " , color , " " , animal , "."
say "They became best friends."
say ""
say "The end."
```

Type a name, a color, and an animal when asked. Notice how the story
changes every time.

## Read the code

```
say "Along the way, they met a " , color , " " , animal , "."
```

This `say` has **five** parts separated by commas:
1. `"Along the way, they met a "` — a string. Note the **trailing space**
   inside the quotes. That space is part of the string.
2. `color` — the variable from earlier.
3. `" "` — a string containing **one space**. (This puts a space
   between the color and the animal.)
4. `animal` — another variable.
5. `"."` — a string with a period.

The comma `,` glues all five pieces into one final string, which is
then printed.

> **Notice:** E does NOT add spaces for you. If you want a space, you
> have to put one in a string somewhere. This is the most common
> beginner mistake.

## Tinker

1. Add a new line that uses all three variables together: a `"My name
   is " , name , ", my color is " , color , ", and my animal is " , animal`.
2. Take out the `" "` between `color` and `animal`. Run it. See how the
   words get smushed together?
3. Take out the trailing space in the first string. Same problem.
4. Try a `say` with no commas at all: just `say "hello"`. That works too.

## Break it on purpose

1. Start a string but forget the closing quote: `say "hello , name`.
   What error?
2. Use `,` without anything before it: `, name`. What error?
3. Use `and` instead of `,`: `say "hello" and name`. Read the error.
   (E thinks you're trying to do `and` as a math/logic thing.)

## Common mistakes

- **Words run together** — You forgot a space. Check the end of each
  string literal.
- **Extra spaces you didn't want** — You have too many spaces. Most
  often: the start of a string has a leading space you didn't intend.
- **E says "I can't do that with these values"** — You might have
  mixed in a number without a comma. (We'll cover that in Lesson 4.)

## Going further

- Make a "mad libs" program. Ask the user for: a name, a place, an
  animal, an adjective, a verb. Then build a story using all five.
  Example prompt: `"Tell me a " , adj , " story about " , name , " who " , verb , "s in " , place , "."`
- Try `say` with just one comma. The output should be a single
  concatenated string with no surprises.

## Exit ticket

Without looking:

1. What's the difference between `say "hello"` and `say "hello" , "world"`?
2. Why do we sometimes need a string that's just `" "` (a single space)?
3. Can you build a sentence with three variables and four string
   pieces? Try it.

If yes, on to Lesson 4 — math!
