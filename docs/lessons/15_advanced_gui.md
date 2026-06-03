# Lesson 15 — Advanced GUI (events, state, turtle control)

**Goal:** Make windows that *do* things — buttons that update labels,
text inputs that get read, and GUI controls that move a turtle.

**Time:** ~35 minutes.

> **This is where GUIs get fun.** In Lesson 8, you made windows that
> looked nice but didn't *do* anything. Now you'll add behavior.
> Every app you've ever used works this way: something happens when
> you click a button.

## Why this works

A GUI without events is like a painting — pretty, but nothing
happens. **Event handlers** are what make apps alive. When the user
clicks a button, the program runs a function. That function can
change labels, read text inputs, move turtles, or do anything else
E can do.

The key idea: **the user triggers the action, not the code.**

## Vocabulary

| Word | What it means |
|------|---------------|
| **event** | Something the user does — clicks a button, types in a box. |
| **handler** | A function that runs when an event happens. |
| **state** | The current values your program is keeping track of. |
| **`when ... clicked`** | The E syntax for attaching a handler to a button. |
| **`text of`** | Reads the current text inside a widget. |

## Demo 1: Interactive counter

Save as `13_advanced_gui.e` and run. Click the button — the count
goes up.

```
let win be window
set win title to "Counter"

let count be 0
let lbl be label "Count: 0" on win
let btn be button "Add 1" on win

set lbl font size to 20
set btn color to "green"

make win place lbl at row 0 and column 0
make win place btn at row 1 and column 0

to update_label
    set count to (count plus 1)
    set lbl text to "Count: ", count
end

make win do update_label when btn clicked

show win
```

## Read the counter code

```
let count be 0
```

This creates a **variable** to keep track of the count. It starts at
0. This is the program's *state* — the thing that changes over time.

```
let lbl be label "Count: 0" on win
```

The label shows the current count. We'll update its text when the
button is clicked.

```
to update_label
    set count to (count plus 1)
    set lbl text to "Count: ", count
end
```

This is the **handler function**. It does two things:
1. Adds 1 to `count`
2. Updates the label's text to show the new count

The `,` in `"Count: ", count` joins the strings together (Lesson 3).

```
make win do update_label when btn clicked
```

This is the key line. It says: "When `btn` is clicked, run the
`update_label` function." The handler is *attached* to the button.

```
show win
```

Show the window. Now the user can click and watch the count go up.

> **Important:** The handler function must be defined *before* the
> `make win do ... when` line, or E won't find it.

## Tinker the counter

1. Change `count plus 1` to `count plus 5`. Each click adds 5.
2. Add a "Subtract 1" button:
   ```
   let btn2 be button "Subtract 1" on win
   make win place btn2 at row 2 and column 0

   to subtract_one
       set count to (count minus 1)
       set lbl text to "Count: ", count
   end

   make win do subtract_one when btn2 clicked
   ```
3. Add a "Reset" button that sets count back to 0.
4. Change the initial count to 100. What happens when you subtract
   below 0? (The count goes negative. That's fine.)

## Demo 2: Turtle control panel

Now let's combine GUI and turtle. This program creates a window with
buttons that control a turtle.

```
let win be window
set win title to "Turtle Remote Control"

let ada be turtle
set ada pen color to "blue"

let forward_btn be button "Forward" on win
let left_btn be button "Turn Left" on win
let right_btn be button "Turn Right" on win
let clear_btn be button "Clear" on win

set forward_btn color to "blue"
set left_btn color to "orange"
set right_btn color to "orange"
set clear_btn color to "red"

make win place forward_btn at row 0 and column 0
make win place left_btn at row 1 and column 0
make win place right_btn at row 1 and column 1
make win place clear_btn at row 2 and column 0

to go_forward
    move ada forward 30
end

to turn_left
    move ada left 30
end

to turn_right
    move ada right 30
end

to clear_all
    make ada restart
end

make win do go_forward when forward_btn clicked
make win do turn_left when left_btn clicked
make win do turn_right when right_btn clicked
make win do clear_all when clear_btn clicked

show win
```

## Read the control panel code

```
let ada be turtle
set ada pen color to "blue"
```

Creates a turtle and sets the pen color. The turtle draws in its
own window; the control panel is a separate window.

```
let forward_btn be button "Forward" on win
let left_btn be button "Turn Left" on win
let right_btn be button "Turn Right" on win
let clear_btn be button "Clear" on win
```

Four buttons, each with a descriptive name and label.

```
set forward_btn color to "blue"
set left_btn color to "orange"
set right_btn color to "orange"
set clear_btn color to "red"
```

Color-coding: blue for forward, orange for turning, red for clear.
Color helps the user know what each button does at a glance.

```
to go_forward
    move ada forward 30
end
```

Each handler is a simple function that does one thing. `go_forward`
moves the turtle 30 pixels. `turn_left` and `turn_right` turn it.
`clear_all` restarts the canvas.

```
make win do go_forward when forward_btn clicked
```

Attach each handler to its button. Now clicking "Forward" runs
`go_forward`, clicking "Turn Left" runs `turn_left`, and so on.

## Tinker the control panel

1. Change `forward 30` to `forward 50`. The turtle takes bigger steps.
2. Add a "Backward" button. Hint:
   ```
   to go_backward
       move ada backward 30
   end
   ```
3. Add a "Change Color" button that cycles the pen color.
4. Add a "Draw Circle" button: `move ada right 360` with a small
   forward step inside a loop.
5. Combine with the counter from Demo 1: show the number of moves
   on a label. (You'll need a `moves` variable that increments in
   each handler.)

## Reading text input with `text of`

You can read what the user typed in a text input. Here's a simple
name greeter:

```
let win be window
set win title to "Greeter"

let name_input be text input "Your name" on win
let greet_btn be button "Greet" on win
let result be label "" on win

set result font size to 18

make win place name_input at row 0 and column 0
make win place greet_btn at row 1 and column 0
make win place result at row 2 and column 0

to do_greet
    let name be text of name_input
    set result text to "Hello, ", name, "!"
end

make win do do_greet when greet_btn clicked

show win
```

```
let name be text of name_input
```

`text of name_input` reads the **current text** inside the text
input widget. Whatever the user typed is now in the `name` variable.

```
set result text to "Hello, ", name, "!"
```

Update the label with a greeting. The `,` joins three pieces into
one string.

## Break it on purpose

1. Define the handler *after* the `make win do` line:
   ```
   make win do update_label when btn clicked

   to update_label
       say "clicked"
   end
   ```
   E says it doesn't know `update_label`. Functions must be defined
   before they're used.

2. Use `text of` on a label instead of a text input:
   ```
   let lbl be label "Hello" on win
   say text of lbl
   ```
   This works — you can read a label's text too. Try it.

3. Forget `clicked` at the end of `make win do handler when btn`:
   E says it expected `clicked`. The event name is required.

4. Try `make win do handler when btn pressed`. E doesn't know
   `pressed` — only `clicked` is supported right now.

## Common mistakes

- **"I don't know what 'update_label' means"** — The handler function
  is defined *after* the `make win do ... when` line. Move the `to`
  block above the `make` line.
- **Label doesn't update** — Check that your `set ... text to` line
  is inside the handler function (indented between `to` and `end`).
- **`text of` returns empty** — The text input might be empty, or
  you spelled the widget name wrong.
- **Turtle and GUI don't appear** — Make sure `show win` is at the
  end. If you have both a turtle window and a GUI window, you need
  `show win` for the GUI (the turtle window opens automatically on
  the first turtle command).

## Going further

### Multiple windows

You can have more than one window:

```
let win1 be window
set win1 title to "Window 1"

let win2 be window
set win2 title to "Window 2"

let btn1 be button "Click me" on win1
let btn2 be button "No, me" on win2

make win1 place btn1 at row 0 and column 0
make win2 place btn2 at row 0 and column 0

show win1
show win2
```

Each window is independent. Buttons on `win1` can only affect widgets
on `win1` (and vice versa), unless you use global variables to share
state between them.

### GUI + turtle combined

Here's a program that draws a shape each time you click a button:

```
let win be window
set win title to "Shape Drawer"

let ada be turtle

let square_btn be button "Draw Square" on win
let circle_btn be button "Draw Circle" on win

make win place square_btn at row 0 and column 0
make win place circle_btn at row 1 and column 0

to draw_square
    set ada pen color to "red"
    move ada forward 50
    move ada right 90
    move ada forward 50
    move ada right 90
    move ada forward 50
    move ada right 90
    move ada forward 50
    move ada right 90
    move ada forward 20
end

to draw_circle
    set ada pen color to "blue"
    repeat 36 times
        move ada forward 5
        move ada right 10
    end
    move ada forward 20
end

make win do draw_square when square_btn clicked
make win do draw_circle when circle_btn clicked

show win
```

Each click draws a new shape next to the last one. The turtle's
position moves forward after each shape so they don't overlap.

## Exit ticket

Without looking:

1. What does `make win do handler when btn clicked` do?
2. How do you read the text inside a text input?
3. Why must the handler function be defined *before* the `make` line?
4. What's the difference between a label and a text input?

If yes, on to Lesson 16 — debugging!
