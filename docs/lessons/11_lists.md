# Lesson 11 — Lists (a row of things)

**Goal:** Store a bunch of values in one variable.

**Time:** ~30 minutes.

## Try first (no screen!)

Ask the student: "Tell me the names of your 3 best friends."

They list them. Now: "Now forget the first one." Easy.

"OK, now I have a new friend named Sam. Add them to the end."

You can do this in your head. **That's a list** — a row of things in
order, and you can add, remove, look up, or count them.

## Vocabulary

| Word | What it means |
|------|---------------|
| **list** | A row of values. Like a row of mailboxes, numbered 0, 1, 2... |
| **index** | The position in the list. E starts counting at **0**, same as Python. |
| **element** | One item in the list. |
| **append** | Add a new item to the end. |
| **size** | How many items are in the list. |

## Demo

Save as `08_lists.e` and run:

```
let friends be [ "Alice" , "Bob" , "Charlie" ]
say "I have " , (size of friends) , " friends."

say friends at 0
say friends at 1
say friends at 2
```

Output:
```
I have 3 friends.
Alice
Bob
Charlie
```

## Read the code

```
let friends be [ "Alice" , "Bob" , "Charlie" ]
```

This makes a list with 3 things in it. Notice the **square brackets**
`[` and `]`. The items are separated by **commas**.

```
say (size of friends)
```

`size of X` gives you the length of the list. We use parentheses
around it because E's "size of" can be confused with subtraction in
some contexts. Better safe than sorry.

> **Key point:** In E, lists start at **0**, like in Python and most
> other languages. `friends at 0` is the first one (Alice).
> `friends at 1` is the second (Bob). `friends at 2` is the third
> (Charlie).

```
say friends at 0
```

`at` looks up a position. "List, give me what's at position 0."

## Adding to a list

```
let pets be [ "dog" , "cat" , "fish" ]
let pets be pets with "hamster" added
let pets be pets with "parrot" added
```

The phrase `with ... added` puts a new item at the end. Notice the
order: `with` comes first, then the value, then `added`. Notice we
have to **store the result back** in `pets`. Just like the counter
in Lesson 9: `let n be n plus 1` — the new value replaces the old.

After the code above, `pets` is `["dog", "cat", "fish", "hamster",
"parrot"]`. Its size is 5.

## Looping over a list

This is the pattern. A loop that runs once for each item in the list:

```
let i be 0
repeat (size of pets) times
    say "  " , (pets at i)
    let i be i plus 1
end
```

- Start counter at 0.
- Run the loop `size of pets` times.
- Each time: print the item at position `i`, then add 1 to `i`.

This works but it's clunky. In Lesson 14 (turtle 2) you'll learn a
cleaner way.

## Tinker

1. Add a 4th and 5th friend to the list. Run. See the count go up.
2. Try to access something that doesn't exist: `say friends at 99`.
   What error?
3. Make a list of numbers: `let scores be [ 95, 80, 76, 100 ]`. Loop
   through and print each, plus the average.
4. Make a list of colors, then set the turtle's pen color to each one
   in turn, drawing a line after each.

## Break it on purpose

1. Forget the closing `]`: `let pets be [ "dog" , "cat"`. Error?
2. Use `at 3` on a 3-element list: `say friends at 3`. Error? (Valid
   indices are 0, 1, 2.)
3. Use `at` on a non-list: `let x be 5` then `say x at 1`. Error?
4. Forget the `with ... added` part: `let pets be pets "hamster"`.
   Error?

## Common mistakes

- **"I tried to get item N from a list of size M"** — You tried to
  read at a position that doesn't exist. The error tells you the
  valid range. `friends at 3` on a 3-element list fails because
  valid indices are 0, 1, 2.
- **"I expected a list"** — You tried to do list stuff on a non-list.
  Maybe you forgot to make a list with `[]`?
- **The list never changes** — You forgot the `let pets be pets with
  ... added` pattern. Just saying `pets with "hamster" added` does
  nothing — the new list isn't stored anywhere.

## Going further

### Bigger example: an inventory

```
let inventory be [ "sword" , "potion" , "shield" ]

let i be 0
repeat (size of inventory) times
    say "  * " , (inventory at i)
    let i be i plus 1
end

say ""
say "You found a key!"
let inventory be inventory with "key" added

say "You drank your potion."
let inventory be inventory with "empty potion bottle" added
```

### Loop pattern: total the list

```
let scores be [ 95 , 80 , 76 , 100 ]
let total be 0
let i be 0
repeat (size of scores) times
    let total be total plus (scores at i)
    let i be i plus 1
end

say "Total: " , total
say "Average: " , (total divided by (size of scores))
```

This pattern (start a total at 0, loop through and add each) is
**incredibly common** in real programs.

## Exit ticket

Without looking:

1. How do you make a list in E? What's the difference between `[1, 2, 3]`
   and `1, 2, 3`?
2. What's the first index of a list in E? (0, 1, or something else?)
3. How do you add an item to a list?
4. Why do we use a counter and a loop to print a list?

If yes, on to Lesson 12 — your own commands (functions)!
