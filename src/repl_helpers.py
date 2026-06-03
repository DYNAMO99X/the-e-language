"""REPL helper utilities for the E language.

Provides file-based history, keyword tab-completion, ANSI colors,
and built-in REPL commands (help, vars, clear).

Zero external dependencies — uses only stdlib + msvcrt on Windows.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.environment import Environment


# ---------------------------------------------------------------------------
# ANSI color helpers
# ---------------------------------------------------------------------------

_SUPPORTS_COLOR = True  # set to False if terminal doesn't support it


def _enable_vt100() -> None:
    """Enable VT100 / ANSI escape processing on Windows 10+."""
    global _SUPPORTS_COLOR
    if os.name != "nt":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        # STD_OUTPUT_HANDLE = -11
        handle = kernel32.GetStdHandle(-11)
        # Get current mode
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        _SUPPORTS_COLOR = False


_enable_vt100()


def _c(code: str, text: str) -> str:
    """Wrap *text* in an ANSI color code. Returns plain text if color
    is not supported."""
    if not _SUPPORTS_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def bold(text: str) -> str:
    return _c("1", text)


def dim(text: str) -> str:
    return _c("2", text)


def cyan(text: str) -> str:
    return _c("36", text)


def green(text: str) -> str:
    return _c("32", text)


def yellow(text: str) -> str:
    return _c("33", text)


def red(text: str) -> str:
    return _c("31", text)


def magenta(text: str) -> str:
    return _c("35", text)


def bright_cyan(text: str) -> str:
    return _c("96", text)


# ---------------------------------------------------------------------------
# File-based history  (~/.e_history)
# ---------------------------------------------------------------------------

_MAX_HISTORY = 500


def _history_path() -> Path:
    return Path.home() / ".e_history"


def load_history() -> List[str]:
    """Load history from ~/.e_history. Returns empty list on failure."""
    path = _history_path()
    if not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        # Trim to max
        if len(lines) > _MAX_HISTORY:
            lines = lines[-_MAX_HISTORY:]
        return lines
    except Exception:
        return []


def save_history_line(line: str) -> None:
    """Append a line to ~/.e_history, keeping the file trimmed."""
    path = _history_path()
    try:
        lines = []
        if path.exists():
            lines = path.read_text(encoding="utf-8").splitlines()
        lines.append(line)
        if len(lines) > _MAX_HISTORY:
            lines = lines[-_MAX_HISTORY:]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except Exception:
        pass  # best effort — don't crash the REPL


# ---------------------------------------------------------------------------
# Tab-completion (for use with readline, or standalone prefix matching)
# ---------------------------------------------------------------------------

E_KEYWORDS: List[str] = [
    # core
    "let", "be", "say", "ask",
    # control flow
    "if", "then", "else", "end", "while", "repeat", "times",
    "for", "each", "in", "to", "return",
    # booleans / nothing
    "true", "false", "nothing",
    # logic
    "and", "or", "not",
    # arithmetic
    "plus", "minus", "times", "mod",
    # comparison
    "is",
    # lists / strings
    "at", "with", "added", "size", "of",
    # turtle
    "turtle", "move", "make", "goto", "set",
    # GUI
    "show", "hide", "window", "label", "button", "text", "input",
    "place", "when", "clicked", "row", "column", "do",
]

E_BUILTINS: List[str] = [
    "ask", "number", "text", "random",
    "uppercase", "lowercase",
]

ALL_COMPLETIONS: List[str] = sorted(set(E_KEYWORDS + E_BUILTINS))


def complete_keyword(text: str) -> List[str]:
    """Return all E keywords/builtins that start with *text* (case-insensitive)."""
    if not text:
        return ALL_COMPLETIONS
    low = text.lower()
    return [w for w in ALL_COMPLETIONS if w.startswith(low)]


# ---------------------------------------------------------------------------
# Custom input() with arrow-key history + tab completion
# ---------------------------------------------------------------------------

def _input_with_history(prompt: str, history: List[str]) -> str:
    """Read a line from the user with:
    - Up/Down arrow to cycle through history
    - Tab to complete keywords
    - Normal typing otherwise

    Uses msvcrt on Windows; falls back to plain input() elsewhere.
    """
    if os.name == "nt":
        return _input_windows(prompt, history)
    return _input_unix(prompt, history)


# -- Windows implementation (msvcrt) --

def _input_windows(prompt: str, history: List[str]) -> str:
    import msvcrt  # type: ignore[import-not-found]

    sys.stdout.write(prompt)
    sys.stdout.flush()

    buf: list[str] = []
    hist_idx = len(history)  # one past the end = "new" input
    saved: Optional[str] = None  # what the user was typing before browsing history
    cursor = 0

    def redraw_line(current: str) -> None:
        """Redraw the input line after a history swap or completion."""
        nonlocal cursor
        # Move to start of line content, rewrite, clear tail
        sys.stdout.write("\r" + prompt + current)
        sys.stdout.write(" " * 20)  # clear any leftover chars
        sys.stdout.write("\r" + prompt + current[:cursor])
        sys.stdout.flush()

    while True:
        ch = msvcrt.getwch()

        # --- Enter ---
        if ch in ("\r", "\n"):
            sys.stdout.write("\n")
            sys.stdout.flush()
            return "".join(buf)

        # --- Ctrl-C ---
        if ch == "\x03":
            raise KeyboardInterrupt

        # --- Ctrl-Z (EOF on Windows) ---
        if ch == "\x1a":
            sys.stdout.write("\n")
            sys.stdout.flush()
            raise EOFError

        # --- Escape sequences (arrows, Home, End, etc.) ---
        if ch == "\xe0" or ch == "\x00":
            ch2 = msvcrt.getwch()

            # Up arrow
            if ch2 == "H":
                if history and hist_idx > 0:
                    if hist_idx == len(history):
                        saved = "".join(buf)
                    hist_idx -= 1
                    buf = list(history[hist_idx])
                    cursor = len(buf)
                    redraw_line("".join(buf))
                continue

            # Down arrow
            if ch2 == "P":
                if history and hist_idx < len(history) - 1:
                    hist_idx += 1
                    buf = list(history[hist_idx])
                    cursor = len(buf)
                    redraw_line("".join(buf))
                elif hist_idx == len(history) - 1:
                    # Going past last history entry → restore what user typed
                    hist_idx = len(history)
                    if saved is not None:
                        buf = list(saved)
                        cursor = len(buf)
                        redraw_line("".join(buf))
                continue

            # Left arrow
            if ch2 == "K":
                if cursor > 0:
                    cursor -= 1
                    sys.stdout.write("\r" + prompt + "".join(buf)[:cursor])
                    sys.stdout.flush()
                continue

            # Right arrow
            if ch2 == "M":
                if cursor < len(buf):
                    cursor += 1
                    sys.stdout.write("\r" + prompt + "".join(buf)[:cursor])
                    sys.stdout.flush()
                continue

            # Home
            if ch2 == "G":
                cursor = 0
                sys.stdout.write("\r" + prompt + "".join(buf)[:cursor])
                sys.stdout.flush()
                continue

            # End
            if ch2 == "O":
                cursor = len(buf)
                sys.stdout.write("\r" + prompt + "".join(buf)[:cursor])
                sys.stdout.flush()
                continue

            # Delete
            if ch2 == "S":
                if cursor < len(buf):
                    buf.pop(cursor)
                    redraw_line("".join(buf))
                continue

            continue  # ignore other escape sequences

        # --- Backspace ---
        if ch in ("\b", "\x7f"):
            if cursor > 0:
                cursor -= 1
                buf.pop(cursor)
                redraw_line("".join(buf))
            continue

        # --- Tab completion ---
        if ch == "\t":
            current = "".join(buf)
            # Find the word being typed (last word before cursor)
            before_cursor = current[:cursor]
            parts = before_cursor.split()
            if parts:
                word = parts[-1]
                matches = complete_keyword(word)
                if len(matches) == 1:
                    # Single match — complete it
                    completed = matches[0]
                    # Replace the word in the buffer
                    word_start = before_cursor.rfind(word)
                    new_before = current[:word_start] + completed
                    remaining = current[cursor:]
                    buf = list(new_before + remaining)
                    cursor = len(new_before)
                    redraw_line("".join(buf))
                elif len(matches) > 1:
                    # Multiple matches — show them and keep current input
                    sys.stdout.write("\n" + "  ".join(matches) + "\n")
                    sys.stdout.write(prompt + "".join(buf))
                    sys.stdout.flush()
            continue

        # --- Regular printable character ---
        if ch.isprintable():
            buf.insert(cursor, ch)
            cursor += 1
            # Optimization: just append if at end (most common case)
            redraw_line("".join(buf))


# -- Unix fallback (plain input) --

def _input_unix(prompt: str, history: List[str]) -> str:
    """On Unix/macOS, try to use readline for history. Falls back to
    plain input()."""
    try:
        import readline  # type: ignore[import-not-defined]
        readline.set_history_length(_MAX_HISTORY)
        for h in history:
            readline.add_history(h)
        return input(prompt)
    except ImportError:
        return input(prompt)


# ---------------------------------------------------------------------------
# REPL commands: help, vars, clear
# ---------------------------------------------------------------------------

def cmd_help() -> None:
    """Print a quick reference for E."""
    print()
    print(bold("  E Language — Quick Reference"))
    print(dim("  " + "—" * 40))
    print()
    print(bold("  Variables"))
    print(f"    {cyan('let')} name {cyan('be')} value        " + dim("create a variable"))
    print(f"    {cyan('set')} name {cyan('to')} value         " + dim("change a variable"))
    print()
    print(bold("  Output"))
    print(f"    {cyan('say')} value               " + dim("print something"))
    print()
    print(bold("  Math"))
    print(f"    {cyan('plus')}  {cyan('minus')}  {cyan('times')}  {cyan('divided')} {cyan('by')}  {cyan('mod')}")
    print(f"    {dim('or use')}  {cyan('+')}  {cyan('-')}  {cyan('*')}  {cyan('/')}")
    print()
    print(bold("  Comparison"))
    print(f"    {cyan('is')} {cyan('greater than')}  {cyan('is less than')}  {cyan('is equal to')}")
    print(f"    {dim('or use')}  {cyan('>')}  {cyan('<')}  {cyan('>=')}  {cyan('<=')}  {cyan('=')}  {cyan('==')}  {cyan('!=')}")
    print()
    print(bold("  Strings"))
    print(f"    {cyan('\"hello\"')}  {cyan('\"world\"')}     " + dim("concat with comma: say \"hi\", \" \", name"))
    print()
    print(bold("  Control flow"))
    print(f"    {cyan('if')} cond {cyan('then')} ... {cyan('end')}")
    print(f"    {cyan('if')} cond {cyan('then')} ... {cyan('else')} ... {cyan('end')}")
    print(f"    {cyan('while')} cond ... {cyan('end')}")
    print(f"    {cyan('repeat')} N {cyan('times')} ... {cyan('end')}")
    print(f"    {cyan('for')} each x {cyan('in')} list ... {cyan('end')}")
    print()
    print(bold("  Functions"))
    print(f"    {cyan('to')} func args ... {cyan('end')}")
    print(f"    {cyan('return')} value")
    print()
    print(bold("  Lists"))
    print(f"    {cyan('let')} names {cyan('be')} {cyan('[')} \"Alice\", \"Bob\" {cyan(']')}")
    print(f"    {cyan('at')} index   {cyan('size of')} list   {cyan('with')} list {cyan('added')}")
    print()
    print(bold("  Turtle"))
    print(f"    {cyan('let')} ada {cyan('be')} {cyan('turtle')}")
    print(f"    {cyan('move')} ada {cyan('forward')} 100   {cyan('move')} ada {cyan('right')} 90")
    print(f"    {cyan('set')} ada {cyan('pen color to')} {cyan('\"red\"')}")
    print()
    print(bold("  GUI"))
    print(f"    {cyan('let')} win {cyan('be')} {cyan('window')}")
    print(f"    {cyan('let')} btn {cyan('be')} {cyan('button')} {cyan('\"Click\"')} {cyan('on')} win")
    print(f"    {cyan('make')} win {cyan('place')} btn {cyan('at')} {cyan('row')} 0 {cyan('and')} {cyan('column')} 0")
    print(f"    {cyan('make')} win {cyan('do')} handler {cyan('when')} btn {cyan('clicked')}")
    print(f"    {cyan('show')} win   {cyan('hide')} win")
    print()
    print(bold("  Builtins"))
    print(f"    {cyan('ask')} {cyan('\"prompt\"')}    {cyan('number')} val    {cyan('text')} val")
    print(f"    {cyan('random')} N    {cyan('uppercase')} s    {cyan('lowercase')} s")
    print()
    print(dim("  " + "—" * 40))
    print(dim("  Tab = complete  Up/Down = history  help / vars / clear / bye"))
    print()


def cmd_vars(env: "Environment") -> None:
    """Print all user-defined variables and their values."""
    print()
    print(bold("  Variables:"))
    found = False
    # Walk up the scope chain to collect all variables
    seen: set[str] = set()
    current_env: Optional["Environment"] = env
    while current_env is not None:
        for name, val in current_env.variables.items():
            if name not in seen:
                seen.add(name)
                found = True
                val_str = _format_value(val)
                print(f"    {cyan(name)} = {val_str}")
        current_env = current_env.parent
    if not found:
        print(dim("    (none)"))

    print()
    print(bold("  Functions:"))
    found = False
    seen_fn: set[str] = set()
    current_env = env
    while current_env is not None:
        for name in current_env.functions:
            if name not in seen_fn:
                seen_fn.add(name)
                found = True
                print(f"    {magenta(name)}()")
        current_env = current_env.parent
    if not found:
        print(dim("    (none)"))
    print()


def _format_value(val: object) -> str:
    """Format a value for display in `vars`."""
    if val is None:
        return dim("nothing")
    if isinstance(val, bool):
        return yellow(str(val))
    if isinstance(val, (int, float)):
        return yellow(str(val))
    if isinstance(val, str):
        return green(f'"{val}"')
    if isinstance(val, list):
        items = ", ".join(_format_value(v) for v in val)
        return f"[{items}]"
    # Turtles, windows, widgets — just show type
    return dim(f"<{type(val).__name__}>")


def cmd_clear() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")
