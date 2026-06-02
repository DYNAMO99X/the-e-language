# Changelog

All notable changes to the E language project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
