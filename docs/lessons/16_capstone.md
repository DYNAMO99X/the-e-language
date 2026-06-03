# Lesson 16 — Capstone: a tiny text adventure

**Goal:** Build a small but complete text adventure game. Use
everything you've learned.

**Time:** This one's longer. Take an hour or two. Don't rush it.

## What you're building

A simple text adventure. The player wakes up in a locked room, has to
find a key, and escape. It's a few rooms, a few items, a few
commands. It uses variables, lists, loops, conditionals, and
functions. Everything from the previous 13 lessons.

It's small. **That's the point.** The capstone is **not** "build a
game like Skyrim." It's "build a game you can finish in an hour, and
that you can show your friends."

## How to use this lesson

This lesson is structured differently from the others. The
**first part** is a working tiny version. It plays. It's not great,
but it works.

After that, there's a list of "extensions" — small additions that
make it more interesting. **You don't have to do all of them.** Pick
two or three that sound fun. Add them. Make the game yours.

Then there's a list of "go further" ideas for if you really get
into it. Those are bigger. Save them for another time.

## Step 0: Plan

From Lesson 15, the four-step plan:

1. **What does it do?** A text adventure where you wake up in a room
   and have to find a key to escape.
2. **What does the user see/do?** The game describes the room.
   They type commands. The game responds. They win or quit.
3. **Chunks:** describe the current room, handle a command, check
   for the key in the inventory.
4. **Data:** `inventory` (a list), `current_room` (a string), `won`
   (a boolean), `moves` (a counter).

## Step 1: The tiny version

Here's a tiny version that plays. Save it as `16_capstone.e`. Read
it. Run it. Try to win.

```
let inventory be [  ]
let won be false
let current_room be "start"
let moves be 0

to describe room
    if room is equal to "start" then
        say ""
        say "=== The Locked Room ==="
        say "You are in a small stone room. There's a wooden door to the north."
        say "On the floor, you see a small brass key."
    else
        if room is equal to "hallway" then
            say ""
            say "=== The Hallway ==="
            say "A long hallway stretches north. Torches flicker on the walls."
            say "There's a locked door to the south (back to the start room)."
        else
            if room is equal to "outside" then
                say ""
                say "=== Outside ==="
                say "You step out into the sunshine. Birds are singing."
                say "You are free!"
            end
        end
    end
end

to has_key items
    let i be 0
    let found be false
    repeat (size of items) times
        if (items at i) is equal to "key" then
            let found be true
        end
        let i be i plus 1
    end
    return found
end

while won is false
    describe current_room

    say ""
    say "Commands: look, take key, go north, go south, inventory, quit"
    let command be ask "> "

    if command is equal to "look" then
        describe current_room
    else
        if command is equal to "take key" then
            if current_room is equal to "start" then
                let inventory be inventory with "key" added
                say "You picked up the brass key."
            else
                say "There's no key here."
            end
        else
            if command is equal to "go north" then
                if current_room is equal to "start" then
                    if has_key inventory then
                        say "You unlock the door and step through."
                        let current_room be "hallway"
                    else
                        say "The door is locked. You need a key."
                    end
                else
                    if current_room is equal to "hallway" then
                        let current_room be "outside"
                        let won be true
                    end
                end
            else
                if command is equal to "go south" then
                    if current_room is equal to "hallway" then
                        let current_room be "start"
                    else
                        say "You can't go that way."
                    end
                else
                    if command is equal to "inventory" then
                        if (size of inventory) is 0 then
                            say "You are carrying nothing."
                        else
                            say "You are carrying:"
                            let i be 0
                            repeat (size of inventory) times
                                say "  * " , (inventory at i)
                                let i be i plus 1
                            end
                        end
                    else
                        if command is equal to "quit" then
                            say "Goodbye!"
                            let won be true
                        else
                            say "I don't understand '" , command , "'. Try: look, take key, go north, go south, inventory, quit"
                        end
                    end
                end
            end
        end
    end

    if command is not equal to "quit" then
        let moves be moves plus 1
    end
end

if current_room is equal to "outside" then
    say "You escaped in " , moves , " moves. Well done!"
end
```

## Step 2: Play it

Run it. Try these commands in order:

```
look
take key
inventory
go north
look
go north
```

You should escape in 5 moves (each non-quit command counts as a move,
including `look`).

Also try:
- `go north` before taking the key. (Door is locked.)
- `take key` in the hallway. (No key there.)
- `go south` in the start room. (Can't go that way.)
- `inventory` when empty. (Shows "nothing".)
- `dance`. (Doesn't understand.)
- `quit`. (Exits gracefully.)

## Step 3: Read the code

Most of the logic is in the `while won is false` loop. Each iteration:

1. Show the player where they are (via the `describe` function).
2. Show the available commands.
3. Read a command.
4. Big `if` chain that matches the command to an action.
5. Increment the move counter (unless they quit).

There are two helper functions: `describe room` (shows a room based
on the `room` parameter) and `has_key items` (checks if `items` is a
list containing `"key"`). These keep the main loop readable.

Note: the `describe` function takes the room as a **parameter** —
the name `room` is just a placeholder. When we call
`describe current_room`, the value of `current_room` is passed in
and the function uses it as `room`.

## Step 4: Make it yours

**Pick at least two of the extensions below. Add them.** The order
goes from "smallest change" to "biggest change". If you're short on
time, just do the first one or two. If you want a real challenge,
do the bigger ones.

### Easy

1. **Add a torch to the hallway.** The player can `take torch`.
   The torch is just for flavor; it doesn't do anything. But the
   description of the room mentions it.
2. **Add a "score" message at the end.** "You escaped in N moves.
   Par is 5. Bonus: 5 - moves tries." Print whether they beat par.
3. **Add a help command.** `help` prints the list of available
   commands.
4. **Add a "look at X" command.** `look at key` describes the key
   in more detail. Just for the items in the start room.
5. **Make the description change after they've taken the key.**
   Once they pick it up, the room description says "the floor is
   empty" instead of "you see a key on the floor."

### Medium

6. **Add a third room.** Between the hallway and outside, add
   "the courtyard". The player has to go through it to win.
7. **Add a second key.** The hallway has a door that needs a
   *different* key. The player has to go back to the start, find
   the second key, and bring it. Make the start room have BOTH keys.
8. **Add "examine" command.** `examine X` for items in the room
   or in the inventory. (You can use `if` chains for the items.)
9. **Save and load.** The player can type `save` to write their
   progress to a file, and `load` to read it back. (Hint: use
   `say` for now to fake it — writing files is in a later lesson.)
10. **Random monster.** Once in a while, a monster appears in the
    hallway. The player can `run` (50% chance of success) or
    `fight` (always wins but loses a move). Use `random 1, 2`.

### Hard (only if you're really into it)

11. **Multiple endings.** Based on the player's moves or items,
    end the game differently. Maybe a "you barely made it" ending
    or a "you found a treasure" ending.
12. **Maze.** Add 5 more rooms connected in a maze. The player
    has to navigate from the start to the outside. Hint: use
    `current_room` to track where they are. The hallway now goes
    east, west, north, south, but only some of those directions
    lead to real rooms.

## Step 5: Tinker

After you've added at least two extensions:

1. **Test it.** Play through your game. Try weird commands. Find
   bugs.
2. **Add a command you wish existed.** If there's something you
   keep wanting to do but can't, add it.
3. **Show someone.** Have a friend play it. Watch them get stuck.
   The things they get stuck on are features to add or improve.

## What you learned

If you did the basic capstone, you used:
- `let` and `say` (Lessons 1, 2)
- `ask`, `number`, and `,` for string concat (Lessons 2, 3)
- `if`, `else`, `is equal to` (Lesson 7)
- `while` and `repeat` (Lesson 8)
- Lists, `size of`, `at`, and `with ... added` (Lesson 9)
- Functions with `to`/`end`, parameters, and `return` (Lesson 10)
- `is not equal to` (Lesson 7)
- Recursion? Not directly, but `has_key` uses a loop with state,
  which is the same idea. (Lesson 11)
- All the debugging skills from Lesson 14
- The four-step plan from Lesson 15

**That's the entire curriculum.** Every concept in E was used in
this game. If you can build this, you can build a lot of things.

## Going further

After you finish the capstone, here are some bigger projects to
try:

- **A number guessing game with a high-score system.** Track the
  fewest moves. Save it to a file.
- **A simple chatbot.** The user types something, the program
  picks a response from a list.
- **A turtle art generator.** The user picks "tree" or "spiral"
  or "fractal" and the turtle draws it.
- **A quiz game.** The program has a list of questions and
  answers. It asks one at a time. Score at the end.
- **A drawing program with the turtle.** Commands: `forward`,
  `turn left`, `turn right`, `pen up`, `pen down`, `color`. The
  user types commands and the turtle draws.

## Exit ticket

Take a step back. Without looking, can you:

1. Describe the structure of the capstone program from memory?
2. Name 3 things in the capstone that use `if`?
3. Name 1 thing that uses a function?
4. What was the **hardest** part of building it? What did you do
   to make it easier?

You finished the curriculum. **That is a real achievement.** Most
people who start learning programming never finish a project. You
did. Now: build more things. The best way to get better is to
write more programs.
