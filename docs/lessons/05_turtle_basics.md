# Lesson 5 — Drawing with the turtle (part 1)

**Goal:** Use the turtle to make your first drawings.

**Time:** ~30 minutes.

> 🎉 **Visual reward lesson!** After four lessons of numbers and
> words, you get to make the computer draw on the screen. If a window
> pops up with a triangle that looks like a UFO, that's normal —
> it's the canvas.

## Try first (no screen!)

Hand the student a pencil and paper. Stand them in the middle of the
paper. Say:
- "You are a turtle. The pencil is your pen."
- "Forward" means take one step in the direction you're facing.
- "Right 90" means turn a quarter turn to your right.

Give them directions one at a time:
- "Forward 5 steps."
- "Right 90."
- "Forward 5 steps."
- "Right 90."
- ... (repeat 4 times total)

They should draw a square. Now: **they are a turtle.** Same idea, but
the computer does the walking.

## Vocabulary

| Word | What it means |
|------|---------------|
| **turtle** | A small drawing cursor that walks around the screen. |
| **canvas** | The area it draws on. Think of it as the paper. |
| **pixel** | One tiny dot on the screen. `forward 100` walks 100 pixels. |
| **heading** | Which direction the turtle is facing. 0° = right, 90° = up, 180° = left, 270° = down. |

## Demo

Save this as `05_turtle_basics.e` and run it:

```
let ada be turtle

move ada forward 100
move ada right 90
move ada forward 100
move ada right 90
move ada forward 100
move ada right 90
move ada forward 100

set ada pen color to "red"
move ada forward 100
```

**A window should pop up** showing a black square with a red line
extending from one corner. (If no window opens, you might be in
"text mode" — that's fine too, see the Going Further section.)

## Read the code

```
let ada be turtle
```

This **creates a turtle** and gives it a name. The name `ada` is
arbitrary — you can use any name you like. The turtle starts in the
middle of the canvas, facing right (0°), with its pen down (drawing).

```
move ada forward 100
```

`move` is the verb. `ada` is the turtle. `forward` is the direction.
`100` is how far to go. Together: walk the turtle 100 pixels in the
direction it's currently facing.

```
move ada right 90
```

`right` is also a direction. `90` is how many degrees to turn. (A
full circle is 360°.)

```
set ada pen color to "red"
```

This is a different verb. `set` changes a **property** of the turtle.
The property is `pen color`. The new value is `"red"`. After this
line, anything the turtle draws will be in red.

## Tinker

1. Change the square's size. Make it 200 instead of 100. Run it.
2. Add another `set ada pen color to "blue"` after the red line.
   Then a `forward 100` more. Now you have a multi-color shape.
3. Try `set ada background to "yellow"`. The canvas itself turns yellow.
4. Change `right 90` to `right 60`. What shape do you get? (Hint:
   360 divided by 60 = 6, so 6 turns of 60 make a hexagon.)

## Draw a triangle

A triangle has 3 sides. The turtle needs to turn 360 ÷ 3 = 120 degrees
at each corner. Try:

```
let ada be turtle
move ada forward 100
move ada right 120
move ada forward 100
move ada right 120
move ada forward 100
```

## Break it on purpose

1. Capitalize `move`: `Move ada forward 100`. What error?
2. Use a number that's too big: `move ada forward 99999999`. The turtle
   goes off-screen. That's not really an error, but is it what you
   wanted?
3. Try `move ada backward 50` instead of `forward`. Notice the turtle
   walks the opposite way.
4. Type the turtle's name wrong: `let ada be turtle` then
   `move adam forward 50`. What does E say? (Hint: it tells you
   there's no turtle called `adam`.)

## Common mistakes

- **"I don't know a turtle called 'ada'"** — You forgot the `let ada
  be turtle` line at the top.
- **"I expected a number"** — You wrote `move ada forward` without
  a number. Always include the distance.
- **The window doesn't appear** — You might be in `--turtle-mode text`.
  Try removing that flag, or check the Going Further section below.

## Going further

### Drawing without a window (text mode)

If you can't open a window — maybe you're on a server, or the window
won't show — you can run the turtle in **text mode**:

```bash
e --turtle-mode text 05_turtle_basics.e
```

In text mode, every command the turtle would have done is printed to
the console instead. Great for learning the language without needing
a display.

### Try these

- A pentagon: 5 sides, turn 72° at each corner. (360 / 5 = 72)
- A house: a square with a triangle on top.
- A staircase: 5 right turns of 90, each followed by a forward step.

## Exit ticket

Without looking:

1. What does `let ada be turtle` do?
2. What's the difference between `forward 50` and `backward 50`?
3. How would you draw a triangle? How many degrees at each corner?

If yes, on to Lesson 8 — GUI basics!
