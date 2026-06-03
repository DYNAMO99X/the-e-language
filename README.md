# E — A programming language that reads like English

> *Personal project. A super-friendly, English-like programming language.*

## What is E?

E is a tiny, easy-to-read programming language designed to feel like you're
writing instructions in plain English. No semicolons. No braces. No mystery.

> **Note:** This is not the [1997 E language](https://en.wikipedia.org/wiki/E_(programming_language))
> by Electric Communities (Mark S. Miller, Douglas Crockford, et al.), which
> was a Java extension for secure distributed computing. This E is a
> separate, beginner-friendly language built in Python.

```e
let name be ask "What is your name? "
let age be ask "How old are you? "

say "Hello, " , name , "!"

if age is greater than 30 then
    say "You are over 30"
else
    say "You are 30 or younger"
end
```

## How to run E

```bash
python e.py examples/hello.e     # run a .e file
python e.py                       # start the REPL
python -m unittest discover tests # run all 214 unit tests
```

## Building a standalone Windows .exe

E can be packaged into a single self-contained Windows executable
(`dist\e.exe`, ~12 MB) with [PyInstaller](https://pyinstaller.org/).
No Python install is required on the target machine.

```bash
pip install pyinstaller
build.bat
```

That runs `pyinstaller e.spec --clean --noconfirm` and drops the
binary into `dist\e.exe`. Test it with:

```cmd
dist\e.exe examples\hello.e
```

### Installing system-wide (Full Package)

Run `install_win64.bat` to:

1. **Copy** `dist\e.exe` to a directory of your choice (default: the
   project root, but you can type any path).
2. **Add that directory to your user PATH** so you can run `e file.e`
   from any terminal. (Uses `HKCU\Environment`, no admin required.)
3. **Register the `.e` file extension** so double-clicking a `.e` file
   in Windows Explorer runs it with the installed `e.exe`.

To uninstall everything (file association, PATH entry, the binary),
run `uninstall_e.bat`.

## Quick taste of the language

```e
-- variables
let name be "Alice"
let count be 0

-- math
let area be 3.14 times 5 times 5

-- choices
if area is greater than 50 then
    say "Big circle"
end

-- loops
repeat 3 times
    say "hi"
end

let fruits be ["apple", "banana", "cherry"]
for each fruit in fruits
    say fruit
end

-- functions
to square x
    return x times x
end

say square 5      -- 25

-- drawing
let ada be turtle
move ada forward 100
move ada right 90
move ada forward 100
set ada pen color to "red"
make ada draw circle 30
```

## Project structure

```
E/
├── e.py                    # Entry point
├── e.spec                  # PyInstaller build config
├── e.ico                   # Icon used by the .exe
├── build.bat               # One-click build script (the .exe)
├── build-extension.bat     # One-click build script (the VSCode ext)
├── install_win64.bat       # Per-user installer (no admin)
├── uninstall_e.bat         # Reverses install_win64.bat
├── src/                    # Interpreter implementation
│   ├── lexer.py            # Source code -> tokens
│   ├── parser.py           # Tokens -> AST
│   ├── interpreter.py      # AST -> execution
│   ├── ast_nodes.py        # AST node classes
│   ├── tokens.py           # Token types
│   ├── environment.py      # Scoped variable storage
│   └── errors.py           # Friendly error messages
├── vscode-e/               # VSCode extension (syntax + run)
├── examples/               # Sample .e programs
├── tests/                  # Unit tests (214 tests)
├── docs/                   # language_tour.md, grammar.md, bridge_to_python.md
│   └── lessons/            # 14-lesson beginner curriculum + capstone
└── README.md
```
E/
├── e.py                    # Entry point
├── e.spec                  # PyInstaller build config
├── e.ico                   # Icon used by the .exe
├── build.bat               # One-click build script
├── install_win64.bat       # Per-user installer (no admin)
├── uninstall_e.bat         # Reverses install_win64.bat
├── src/                    # Interpreter implementation
│   ├── lexer.py            # Source code -> tokens
│   ├── parser.py           # Tokens -> AST
│   ├── interpreter.py      # AST -> execution
│   ├── ast_nodes.py        # AST node classes
│   ├── tokens.py           # Token types
│   ├── environment.py      # Scoped variable storage
│   └── errors.py           # Friendly error messages
├── examples/               # Sample .e programs
├── tests/                  # Unit tests (214 tests)
├── docs/                   # language_tour.md, grammar.md, bridge_to_python.md
│   └── lessons/            # 14-lesson beginner curriculum + capstone
└── README.md
```

## Documentation

- **[docs/language_tour.md](docs/language_tour.md)** — Beginner-friendly
  walkthrough of the entire language with examples (includes a full
  section on the turtle).
- **[docs/grammar.md](docs/grammar.md)** — Formal grammar reference.
- **[docs/lessons/](docs/lessons/)** — A 14-lesson curriculum + capstone
  for teaching E to beginners. Each lesson has a teacher's guide and
  a matching starter `.e` file.
- **[docs/bridge_to_python.md](docs/bridge_to_python.md)** — A
  E-to-Python cheat sheet for when you want to learn Python after E.
- **[vscode-e/](vscode-e/)** — A small VSCode extension that adds
  syntax highlighting and a "Run File" command (Ctrl+F5) for `.e`
  files. Build it with `build-extension.bat` and install the resulting
  `.vsix` with `code --install-extension`.

## Example programs

- `examples/hello.e` — Hello, world
- `examples/calculator.e` — Interactive calculator
- `examples/guessing_game.e` — Number guessing game
- `examples/functions.e` — Function demos
- `examples/fibonacci.e` — Lists + recursion

## Project status

✅ All 10 implementation phases complete. The language is feature-complete
for the personal-project scope:

- Variables, math, comparisons, logic
- if/else (with else-if chain) / while / repeat / for-each
- Functions with parameters, return values, recursion
- Lists with index, size, append
- Built-in functions: ask, number, text, uppercase, lowercase, random
- Three equivalent string delimiters: `"`, `'`, `` ` ``, with full escape support
- Built-in turtle drawing (`let ada be turtle`, `move`, `make`, `set`, `goto`)
- Interactive REPL with `Hi! Ready to code?` greeting
- Single-file Windows `.exe` build (PyInstaller)
- 214 unit tests across lexer, parser, interpreter, and turtle
- Friendly English-style error messages
- 14-lesson beginner curriculum + capstone (in `docs/lessons/`)
- E-to-Python bridge document (in `docs/bridge_to_python.md`)

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
