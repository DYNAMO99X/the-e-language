# Lesson 11 — Recursive patterns with the turtle (turtle 2)

**Goal:** Use recursion to make beautiful, surprising pictures.

**Time:** ~35 minutes.

> **This is the most fun lesson.** A few lines of code can make
> amazing patterns. Don't be afraid to play.

## Why this works

In Lesson 5, we used loops to draw shapes. Loops are great for
repeating the same thing many times. But what if the **pattern itself
gets smaller** as you go? That's when you need recursion.

A tree branch: a stem, then two smaller branches, then two smaller
branches, then two smaller branches. Recursion handles that naturally.

## Demo 1: A spiral

Save as `11_turtle_recursive.e` and run. You'll see a tree and a
spiral (the `say` lines help you tell them apart).

```
to draw_spiral bob length angle
    if length is less than 5 then
        return
    end
    set bob pen color to "blue"
    move bob forward length
    move bob right angle
    draw_spiral bob, (length times 0.95), angle
end

let bob be turtle
move bob left 90
move bob backward 50
draw_spiral bob, 100, 91
```

## Read the spiral code

```
to draw_spiral bob length angle
    if length is less than 5 then
        return
    end
    move bob forward length
    move bob right angle
    draw_spiral bob, (length times 0.95), angle
end
```

- **Parameters:** `bob` is the turtle's name; `length` is how long to
  go this round; `angle` is how much to turn.
- **Base case:** if `length` is less than 5, stop. The spiral gets
  too small to see.
- **Recursive case:** go forward, turn, then call ourselves with a
  slightly smaller length (95% of what it was).

The key is `length times 0.95`. Each round, the line gets 5% shorter.
A thousand calls later, it's under 5 and stops. The pattern that
emerges is a smooth spiral.

> **A word on turtle names:** `turtle` is a reserved word in E
> (because it's the keyword for creating one), so we can't use it as
> a parameter name. Use the turtle's actual name (`ada`, `bob`, etc.)
> as the parameter. That means your function will only work with
> that one turtle. For most lessons that's fine.

## Tweak the spiral

- Change `0.95` to `0.99`. The spiral goes much longer.
- Change `0.95` to `0.8`. It tightens up faster.
- Change `91` to `90`. The pattern is a regular polygon (sides
  get shorter? wait no, sides get shorter, but they don't curve).
- Change `91` to `89`. The spiral goes the other way.

## Demo 2: A fractal tree

```
to draw_tree ada depth length
    if depth is 0 then
        return
    end
    set ada pen color to "brown"
    move ada forward length

    move ada left 30
    draw_tree ada, (depth minus 1), (length times 0.7)

    move ada right 60
    draw_tree ada, (depth minus 1), (length times 0.7)

    move ada left 30
    move ada backward length
end

let ada be turtle
move ada left 90
move ada backward 100
draw_tree ada, 8, 80
```

## Read the tree code

```
to draw_tree ada depth length
    if depth is 0 then
        return
    end
```

`depth` is how many levels of branching we have left. When it hits 0,
stop. (Like the spiral's `length < 5`, but with a different number.)

```
    set ada pen color to "brown"
    move ada forward length
```

Draw the trunk. We can change the pen color to brown to make it look
more tree-like. (You could do per-depth color too!)

```
    move ada left 30
    draw_tree ada, (depth minus 1), (length times 0.7)
```

Turn left 30°. Now draw a smaller branch off the left. The new branch
is 70% as long as the parent (because of `length times 0.7`).

```
    move ada right 60
    draw_tree ada, (depth minus 1), (length times 0.7)
```

To go from facing 30° left of "up" to 30° right of "up", we turn
**right 60°** (30° back to up, then 30° more to the right).

```
    move ada left 30
    move ada backward length
```

Now we need to **back to the start of the branch** with the same
heading. We turn left 30° (back to up), then walk backward the same
distance. This is called "unwinding" the recursion — restoring the
turtle's state so the next branch starts in the right place.

## Why the unwinding matters

Each call to `draw_tree` ends with the turtle **in the same position
and heading** as when it started. So when the right branch finishes,
we're back at the trunk, ready to draw the next part.

This is a key insight: **recursive functions should clean up after
themselves**. If they don't, the turtle ends up in weird spots.

## Tinker

1. Change the angle `30` to `45` in the tree. Wider branches.
2. Change the scale `0.7` to `0.5`. Skinnier, longer branches.
3. Add leaves: at the very tip (when depth is 1), draw a small
   square or use a different color. Hint:
   ```
   if depth is 1 then
       set ada pen color to "green"
       move ada forward 10
       move ada backward 10
       set ada pen color to "brown"
       return
   end
   ```
4. Make a 3-branch tree: split into 3 instead of 2. (Left 30, draw,
   right 60 to center, then right 30 more for the third. Then back
   to start.)
5. Make a "Koch snowflake" (look it up — it's a famous fractal).

## Break it on purpose

1. Forget to `return` at the base case. The function will keep
   calling itself with `depth = 0`. The base case doesn't help if
   you don't return.
2. Forget the `backward length`. The tree branches will accumulate
   forward steps and end up off the canvas.
3. Use `depth` instead of `depth minus 1` in the recursive call.
   Infinite recursion.
4. Try `draw_tree ada, 50, 80` (depth 50). It will run for a long
   time. The `say` lines are the only way to tell when it's done.

## Common mistakes

- **Tree draws, but the branches go off the screen** — Make `length`
  smaller or `depth` smaller. The first time I tried this, my
  branches ended up in another ZIP code.
- **Turtle ends up in a weird place after the function ends** — You
  forgot the `backward length` or one of the `left 30` / `right 60`.
- **The recursion never ends** — `depth` isn't getting smaller.

## Going further

### Color by depth

```
to color_tree ada depth length
    if depth is 0 then
        return
    end
    if depth is greater than 4 then
        set ada pen color to "brown"
    else
        if depth is greater than 2 then
            set ada pen color to "darkgreen"
        else
            set ada pen color to "lime"
        end
    end
    move ada forward length
    move ada left 30
    color_tree ada, (depth minus 1), (length times 0.7)
    move ada right 60
    color_tree ada, (depth minus 1), (length times 0.7)
    move ada left 30
    move ada backward length
end
```

Different colors for the trunk, middle branches, and tips. Now it
looks like a real tree in spring.

### Snowflake / fern

Look up the **Barnsley fern**. It's a famous fractal that uses
recursion and randomness. Or the **Koch snowflake** — at each step,
replace the middle third of a line with two sides of a triangle.

## Exit ticket

Without looking:

1. Why does the spiral need a `length` that gets smaller each call?
2. Why does the tree need a `backward length` at the end?
3. What would happen if the base case `depth is 0` was missing?
4. Can you write a function that draws a square using recursion? (You
   might not need it, but it's good practice.)

If yes, on to Lesson 12 — reading errors and debugging!
