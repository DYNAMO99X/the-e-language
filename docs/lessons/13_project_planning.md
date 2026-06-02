# Lesson 13 — Planning a small project

**Goal:** Take an idea and turn it into a working program, step by
step. Combine everything you've learned.

**Time:** ~30 minutes. (Then you can start Lesson 14!)

## The problem with big projects

When a program is small (a few lines), you can just write it
straight through. When it's big (100+ lines), that doesn't work
anymore. You'll lose track. You'll write the same code twice. You'll
forget what your variables mean.

**The fix:** plan before you code.

## The four-step plan

### Step 1: What does it do?

Write one sentence: what does this program do? Keep it short.

Examples:
- "A tip calculator that asks for a bill and prints the total with
  tip."
- "A game where the user has to guess a number between 1 and 100."
- "A turtle that draws a snowflake."

If you can't write this in one sentence, your project is too big. Cut
it down.

### Step 2: What does the user see / do?

Make a list of every interaction the user has with the program.

For a tip calculator:
- The program asks "How much was the bill?"
- The user types a number
- The program says "Tip: $X" and "Total: $Y"
- The program ends

For a guess-the-number game:
- The program picks a secret number (1-100)
- The program says "Guess a number"
- The user types a guess
- The program says "Higher" or "Lower" or "You got it!"
- If they didn't get it, go back to "Guess a number"
- If they did, the program ends

This list is your program's **interface**. It's the contract between
the user and the code.

### Step 3: What chunks of code do I need?

For a guess-the-number game:
1. Pick a random number
2. Loop: ask for a guess, give feedback, stop when correct
3. Tell them if they got it on the first try (or how many tries)

Each of those is a chunk. Some of them are short (1-2 lines) and
some are longer (5-10 lines). The chunks don't have to be functions,
but it's a good idea to think of them that way. It makes them
reusable.

### Step 4: What data do I have?

Variables and lists. For a guess-the-number game:
- `secret` — the number the user is trying to guess
- `guess` — the number they typed
- `tries` — how many guesses so far

This is your **state** — what the program "remembers" as it runs.

## The "scratch" method

Don't try to write the whole program in one go. **Write it in
scratches.**

1. Write a tiny version of the program that does the bare minimum.
   For a guess-the-number game, that might be:
   ```
   let secret be 42
   say "The secret is 42. Can you guess it?"
   let guess be ask "Your guess: "
   let guess be number guess
   if guess is equal to secret then
       say "You got it!"
   else
       say "Wrong."
   end
   ```
2. Run it. Make sure the basic flow works.
3. Add one feature. Maybe now: only let the user guess once, and
   tell them higher/lower.
4. Run again. Make sure that part works.
5. Add the loop. Let them keep guessing.
6. Run again. Does the loop work?
7. Add a counter for tries. Print it at the end.

**Each step is a tiny program that runs.** You're never more than
5 minutes from a working version. If something breaks, you know
exactly which step broke it.

This is the **opposite** of "write the whole thing, then debug for
an hour." If you build it up bit by bit, you almost never have big
mysteries.

## The temptation of the "perfect" plan

You'll be tempted to spend an hour on Step 1, writing the perfect
spec, before you write any code. **Resist this.** Get something
running as fast as possible, even if it's tiny. A working tiny
thing is more useful than a perfect unfinished thing.

## Example: a tiny adventure game

### Step 1

"A text adventure where you wake up in a room and can look around,
take items, and try to leave."

### Step 2

- Game describes the room
- Player types a command: "look", "take key", "go north", "quit"
- Game responds based on the command
- Player has to find a key to open the door
- Once they do, they "win"

### Step 3

1. Print a description of the room
2. Read a command from the player
3. Match the command: look, take, go, quit
4. Update the game state (e.g., key is in the inventory)
5. Loop until the player wins or quits

### Step 4

- `inventory` — list of items the player has
- `room` — where they are (just one room for now)
- `won` — boolean for whether they've won

This is Lesson 14's capstone. Let's just sketch it here:

```
let inventory be [  ]
let won be false

while won is false
    say "You are in a dark room. There is a door to the north."
    say "On the floor you see: a small key."
    say "What do you do?"

    let command be ask "> "

    if command is equal to "look" then
        say "There's a small key on the floor."
    else
        if command is equal to "take key" then
            let inventory be inventory with added "key"
            say "You picked up the key."
        else
            if command is equal to "go north" then
                if (size of inventory) is greater than 0 then
                    say "You unlock the door and escape!"
                    let won be true
                else
                    say "The door is locked. You need a key."
                end
            else
                if command is equal to "quit" then
                    let won be true
                else
                    say "I don't understand that."
                end
            end
        end
    end
end

say "Goodbye!"
```

(That's not perfect, but it's a working tiny version. We can add
features in Lesson 14.)

## Tinker

1. Pick a small project you'd like to build. Walk through the four
   steps **on paper**. Don't write code yet. Just plan.
2. Then build the **smallest working version** you can. Run it.
3. Add one feature. Run it.
4. Add another. Run it.
5. Show it to a friend.

## Common planning mistakes

- **The project is too big** — Cut it in half. Cut it in half again.
  If it can be done in 100 lines, it's a good first project.
- **You can't describe what happens** — If you can't list the user's
  interactions, you're not ready to code yet. Keep planning.
- **You plan features you'll never build** — Be realistic. "Add
  multiplayer support" is **not** a first-project feature.

## Going further

- **Show your work.** Find a friend, family member, or online
  community and demo your project. Explaining it to someone else
  will reveal bugs and new ideas.
- **Get feedback.** "What was confusing? What would you add?"
- **Iterate.** Now that you have something, what's the next thing
  to add? What's the most important one?

## Exit ticket

Without looking:

1. What's the four-step plan?
2. Why is "build it tiny, then grow" better than "write it all, then
   debug for hours"?
3. What's one project you'd like to build?

If yes, on to Lesson 14 — your first real project!
