# Lesson 8 — GUI basics (windows, buttons, labels)

**Goal:** Build simple GUI windows with buttons, labels, and text inputs.

**Time:** ~30 minutes.

> **Your first app!** After drawing with the turtle, you get to make
> something the user can *click*. This is how real apps start — a
> window, some buttons, some text. E uses tkinter under the hood, but
> you don't need to know that.

## Try first (no screen!)

Hand the student a blank sheet of paper. Say: "Design your dream app.
Draw a window. What's in it? A title? A button? A place to type?"

Let them sketch for 2 minutes. Then say: "Now we're going to build
that — in code."

## Vocabulary

| Word | What it means |
|------|---------------|
| **window** | A blank box on the screen. Everything else goes inside it. |
| **widget** | A thing inside a window — a button, a label, a text input. |
| **label** | Text that the user reads but can't click or type in. |
| **button** | Something the user clicks. |
| **text input** | A box where the user types something. |
| **grid** | The layout system. Widgets go in rows and columns, like a table. |
| **row** | A horizontal line in the grid. |
| **column** | A vertical line in the grid. |

## Demo

Save this as `06_gui_basics.e` and run it:

```
let win be window
set win title to "My First App"

let greeting be label "Hello, world!" on win
let name be text input "Type your name here" on win
let btn be button "Say hi" on win

set greeting font size to 16
set btn color to "blue"

make win place greeting at row 0 and column 0
make win place name at row 1 and column 0
make win place btn at row 2 and column 0

show win
```

**A window should pop up** with a title, a label, a text input, and a
blue button. (If no window opens, you might be in text mode — see the
Going Further section.)

## Read the code

```
let win be window
```

This **creates a window** and gives it a name. Same idea as `let ada
be turtle` — you're making something and naming it.

```
set win title to "My First App"
```

Sets the **title** — the text that appears in the title bar at the
top of the window.

```
let greeting be label "Hello, world!" on win
```

Creates a **label** (read-only text) and puts it on the window. The
`"Hello, world!"` is the text it displays. The `on win` part says
which window to put it on.

```
let name be text input "Type your name here" on win
```

Creates a **text input** — a box the user can type in. The
`"Type your name here"` is the default text inside the box.

```
let btn be button "Say hi" on win
```

Creates a **button** with the text "Say hi" on it.

```
set greeting font size to 16
```

Changes a property of the label — makes the text bigger. You can
set `font size`, `color`, `text`, and more.

```
make win place greeting at row 0 and column 0
make win place name at row 1 and column 0
make win place btn at row 2 and column 0
```

This is the **grid layout**. Think of it like a spreadsheet:
- `row 0, column 0` = top-left cell (the label)
- `row 1, column 0` = one cell down (the text input)
- `row 2, column 0` = two cells down (the button)

All three widgets are in column 0, stacked vertically.

```
show win
```

Makes the window visible. Without this, the window exists but
you can't see it.

## Tinker

1. Change the title: `set win title to "Calculator"`. Run it.
2. Add a second label: `let sub be label "Welcome!" on win`. Place
   it at `row 0 and column 1` (next to the first label).
3. Change the button color to `"red"` or `"green"`.
4. Change the font size to `24`. What happens? (It gets bigger.)
5. Add a second button: `let btn2 be button "Cancel" on win`. Place
   it at `row 3 and column 0`.

## Draw a shape with widgets

Can you make a window that looks like this?

```
[ Name:  ____________ ]
[ Email: ____________ ]
[        Submit       ]
```

Try:

```
let win be window
set win title to "Sign Up"

let name_label be label "Name:" on win
let name_input be text input "" on win
let email_label be label "Email:" on win
let email_input be text input "" on win
let submit be button "Submit" on win

make win place name_label at row 0 and column 0
make win place name_input at row 0 and column 1
make win place email_label at row 1 and column 0
make win place email_input at row 1 and column 1
make win place submit at row 2 and column 0

show win
```

## Break it on purpose

1. Forget `on win`: `let btn be button "Click"`. What error do you
   get? (E doesn't know which window to put it on.)
2. Use `nothing` as the window: `let btn be button "Click" on nothing`.
   What does E say?
3. Skip `show win`. The window is created but never appears.
4. Place two widgets in the same cell: `row 0 column 0` for both a
   label and a button. What happens? (One covers the other.)

## Common mistakes

- **"I don't know a turtle called 'win'"** — You wrote `set win title`
  before `let win be window`. Create the window first.
- **"I can't create a button on 'nope'"** — The window name in `on win`
  doesn't match any window you created.
- **The window doesn't appear** — You forgot `show win` at the end.
- **Widgets overlap** — Two widgets in the same row/column. Change
  the row or column number.

## Going further

### Text mode (no window)

If you can't open a window, run in text mode:

```bash
e --turtle-mode text 06_gui_basics.e
```

In text mode, every GUI command is printed to the console instead.
The window is created in memory but never shown on screen. Great for
testing and learning without a display.

### Turtle and GUI together

You can use the turtle and GUI in the same program:

```
let ada be turtle
let win be window
set win title to "Drawing App"

let draw_btn be button "Draw square" on win
make win place draw_btn at row 0 and column 0

show win
```

The turtle draws in its own window; the GUI has its own window.
They're independent. (We'll explore this more in Lesson 15.)

## Exit ticket

Without looking:

1. What does `let win be window` create?
2. How do you put a button on a window?
3. What's the difference between a label and a text input?
4. How does the grid layout work? What does `row 1 and column 0` mean?

If yes, on to Lesson 9 — making choices!
