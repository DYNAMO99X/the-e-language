# Lesson 0 — Setting up

**Goal:** Get E installed and run your first program.

**Time:** ~15 minutes.

## Vocabulary

| Word | What it means |
|------|---------------|
| **terminal** | A text window where you type commands. On Windows, search for "Command Prompt" or "PowerShell". On Mac, search for "Terminal". |
| **folder** | A place to keep your files. Like a drawer. |
| **file extension** | The little letters at the end of a filename, like `.e` or `.txt`. They tell the computer what kind of file it is. |
| **run** | To ask the computer to actually do what the program says. |

## Step 1: Install E

You have two options. Pick the one that matches your situation.

### Option A: I have a `.exe` and just want to run it (recommended)

If you have `e.exe` (or someone gave you the `e.exe` file), you can skip
the rest of this step. You're done. Just remember where the file is.

### Option B: I want to install it from source (more advanced)

You need Python 3.9 or newer. If you don't have Python yet, get it
from [python.org](https://python.org/downloads/). During install, make
sure to check "Add Python to PATH".

Then open a terminal and type:

```bash
git clone <the-e-repo-url>
cd E
pip install -r requirements.txt
```

You should see no error messages. If you see red text, copy the error
and ask for help.

## Step 2: Make a folder for your programs

In your terminal, type:

**Windows (PowerShell):**
```powershell
mkdir MyEPrograms
cd MyEPrograms
```

**Mac / Linux:**
```bash
mkdir MyEPrograms
cd MyEPrograms
```

This creates a new folder called `MyEPrograms` and moves you inside it.

## Step 3: Open a text editor

You'll need a place to type your programs. **Do not use Microsoft Word
or Google Docs** — they add hidden formatting that breaks programs.

Good choices (free):
- **Windows:** Notepad (already installed), or download [VS Code](https://code.visualstudio.com/)
- **Mac:** TextEdit (set it to "Plain Text" mode), or [VS Code](https://code.visualstudio.com/)
- **Anywhere online:** [vscode.dev](https://vscode.dev) (works in the browser)

Open your editor, then create a new file.

## Step 4: Write your first program

Type this **exactly** (the quotes and capital S matter):

```
say "Hello, world!"
```

Save the file as `hello.e` inside the `MyEPrograms` folder. Make sure
the file ends in `.e`, not `.e.txt` or `.txt`.

## Step 5: Run it

In your terminal (still inside the `MyEPrograms` folder), type:

**If you have the .exe:**
```bash
e hello.e
```

**If you installed from source:**
```bash
python e.py hello.e
```

You should see:

```
Hello, world!
```

🎉 **You just ran your first program.** Show someone.

## Tinker

1. Change `Hello, world!` to your name. Run it again. Does it change?
2. Add a second line: `say "I am learning E"`. What happens?
3. What happens if you forget the closing quote? Try it and read the
   error message.

## Common mistakes

- **"The system cannot find the file specified"** — You're in the wrong
  folder. Use `cd` to go to the right one, or just type the full path
  to the file.
- **The editor saved it as `hello.e.txt`** — The editor added a
  hidden `.txt` at the end. In Notepad, when you save, type the
  filename in quotes: `"hello.e"`. In VS Code, just make sure the
  "Save as type" is set to "All Files".
- **"e is not recognized"** — Your `e.exe` isn't on the PATH. Either
  run it with the full path (e.g. `C:\Users\you\e.exe hello.e`) or
  run `install_win64.bat` to add it.

## Exit ticket

Without looking back at the lesson, can you:

1. Open your terminal and go to your `MyEPrograms` folder?
2. Run `e hello.e` (or `python e.py hello.e`)?
3. Make the program say something different?

If yes to all three, you're ready for Lesson 1.
