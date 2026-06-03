# Changelog

All notable changes to the E language project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-06-03

### Added
- Web requests feature: fetch data from the internet
  - `get "url"` — HTTP GET request
  - `post "url", body` — HTTP POST request
  - `status of resp` — HTTP status code (200 = OK)
  - `body of resp` — response text
  - `timeout 5` — optional timeout (default 10 seconds)
- JSON parsing: work with structured data
  - `json parse text` — convert JSON text to E value
  - `json of resp` — shorthand for `json parse body of resp`
  - `json keys obj` — get keys of a JSON object
  - `json value obj, key` — get a value by key
  - `json of value` — convert E value back to JSON text
- JSON objects map to E as list-of-pairs: `[["key", "value"]]`
- `timeout` keyword with `TimeoutValuePair` AST node for named args
- `src/web.py` — HTTP GET/POST, JSON helpers (stdlib only: `urllib` + `json`)
- 20+ new tests for web/JSON features (mocked HTTP)
- 3 new curriculum lessons (19 total):
  - Lesson 7: Web Requests (basic `get`/`post`)
  - Lesson 17: JSON Parsing
  - Lesson 18: Real API Project

### Changed
- Curriculum expanded from 16 to 19 lessons
- Lessons 06–16 renumbered to 08–19 to make room for new lessons
- All cross-references updated across all lesson files

### Fixed
- Parser: `_parse_call_arg` now handles `timeout <value>` as named-arg pair via `TimeoutValuePair`
- Parser: `_parse_ident_or_call` accepts `allow_call` parameter to prevent nested function calls inside call arguments
- Interpreter: `_eval_call` expands `TimeoutValuePair` to keyword + value args

## [0.3.0] - 2026-06-03

### Added
- GUI windows feature: create and control GUI windows from E code using tkinter under the hood
  - `let win be window` — create a new GUI window
  - `let btn be button "Click Me" on win` — create widgets (button, label, text input)
  - `set win title to "My App"` / `set btn font size to 16` / `set lbl text to "Hello"` — set properties
  - `make win place btn at row 0 and column 0` — grid layout
  - `make win do on_click when btn clicked` — event handlers
  - `show win` / `hide win` — show/hide windows
  - `text of name` — read widget text values
- Text-mode fallback for GUI (works headless, no display needed)
- 29 new GUI tests (272 total)
- `gui_runtime.py` — WindowManager + widget wrappers, tkinter backend + text-mode logging
- `text of` multi-word keyword (tokenizer + parser support)

### Fixed
- Parser: `_expect` already advances, so `_parse_widget_create` no longer double-advances past `on`
- Parser: `_parse_set_property` now handles `font size` (SIZE token, not just IDENT)
- Parser: `_parse_place_widget` and `_parse_handle_event` read identifiers directly instead of `_parse_expression()` which greedily consumed `at`/`and`/`clicked`
- Interpreter: `_exec_set` now falls back to GUI property setting when turtle lookup fails
- Interpreter: `_exec_let` handles `WidgetCreate` statements directly
- `gui_runtime.py`: `set_property` updates widget `text` in both text and window modes

### Added
- `+`, `-`, `*`, `/` as arithmetic operators alongside English keywords (`plus`, `minus`, `times`, `divided by`)
- Web playground with Monaco editor, SVG turtle canvas, Pyodide runtime, 5 built-in examples
- Help modal (`?` button) with quick reference, limitations, and download CTA
- Draggable dividers to resize editor, turtle canvas, and output panels
- Rotating fun loading messages while Pyodide initializes
- 6 new unit tests for symbol arithmetic operators (243 total)

### Fixed
- Playground: replaced `ask`-based examples with hardcoded values (no stdin in browser)
- Playground: replaced `repeat count` with manual counter (not implemented in E interpreter)
- Playground: disable AMD loader during Pyodide init to fix `stackframe` 404 conflict with Monaco

## [0.2.0] - 2026-06-02

### Fixed
- Bumped CI actions to Node.js 24-compatible versions (`checkout@v5`, `setup-python@v6`) before the June 16, 2026 deadline
- Pinned Windows CI runner to `windows-2025-vs2026` to stop silent redirect notices

### Changed
- Added clarification in README that this E is not the 1997 E language by Electric Communities
- Added symbol comparison operators (`>`, `<`, `>=`, `<=`, `=`, `==`, `!=`) as alternatives to English keywords

## [0.1.0] - 2026-06-02

### Added
- **E language core** — lexer, parser, interpreter, and environment
  (variables, arithmetic with English keywords, control flow, functions, lists)
- **String handling** — three interchangeable quote types (`"`, `'`, `` ` ``)
  with cross-quote escapes
- **Turtle graphics runtime** — named turtles (e.g. `ada`, `bob`) with
  window mode (pygame) and headless text mode fallback
- **REPL** with multi-line statement support and `Hi! Ready to code?` greeting
- **Windows `.exe`** built with PyInstaller, per-user installer/uninstaller
  (no admin required), custom teal `e.ico` icon
- **214 unit tests** (lexer, parser, interpreter, turtle)
- **Example programs** in `examples/` — `hello.e`, `guessing_game.e`,
  `shopping_list.e`, `fibonacci.e`, `name_spiral.e`, `dragon.e`,
  `koch_snowflake.e`, `spirograph.e`
- **14-lesson beginner curriculum** in `docs/lessons/` (lessons 0–14)
  covering setup, output, variables, strings, math, turtle basics,
  choices, loops, lists, functions, recursion, recursive turtle art,
  debugging, project planning, and a capstone escape-the-maze game
- **`docs/language_tour.md`** — complete language reference
- **`docs/bridge_to_python.md`** — E→Python cheat sheet for new learners
- **VSCode extension v0.1.0** (`vscode-e/`) — TextMate grammar with
  longest-match multi-word keywords, syntax highlighting for all three
  string types, Ctrl+F5 to run, configurable Python/script paths

### Notes
- This is the initial public release.
- `.vsix` files are built in CI and attached to GitHub Releases, not
  committed to the repository.
- The interpreter is pure Python (standard library only).
