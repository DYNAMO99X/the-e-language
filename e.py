"""E — A programming language that reads like English.

Entry point. Use:
    python e.py file.e        -> run a .e file
    python e.py               -> start the REPL

Flags:
    --turtle-mode MODE        -> auto (default), window, or text
    --help                    -> show usage
"""

import sys
from pathlib import Path


TURTLE_MODES = ("auto", "window", "text")


def _print_usage() -> None:
    print("Usage: e <file.e> [flags]")
    print()
    print("Flags:")
    print("  --turtle-mode MODE   Set turtle mode: auto, window, or text.")
    print("                       auto (default) opens a window if possible,")
    print("                       otherwise logs commands to the console.")
    print("  --help               Show this help message.")
    print()
    print("Run a file:    e examples/hello.e")
    print("Start REPL:    e")


def _parse_args(argv: list) -> tuple:
    """Extract the file path (if any) and CLI flags.

    Returns (file_path_or_None, turtle_mode).
    """
    file_path = None
    turtle_mode = "auto"
    i = 1  # skip program name
    while i < len(argv):
        a = argv[i]
        if a == "--turtle-mode":
            if i + 1 >= len(argv):
                print("E: --turtle-mode needs a value (auto, window, or text).")
                sys.exit(1)
            mode = argv[i + 1].lower()
            if mode not in TURTLE_MODES:
                print(f"E: --turtle-mode must be one of {TURTLE_MODES}, got {mode!r}.")
                sys.exit(1)
            turtle_mode = mode
            i += 2
            continue
        if a == "--help" or a == "-h":
            _print_usage()
            sys.exit(0)
        if a.startswith("--"):
            print(f"E: I don't know the flag '{a}'. Try --help.")
            sys.exit(1)
        # First non-flag is the file path
        if file_path is None:
            file_path = a
            i += 1
            continue
        print(f"E: Unexpected argument '{a}'. Try --help.")
        sys.exit(1)
    return file_path, turtle_mode


def run_file(path: str, turtle_mode: str = "auto") -> int:
    """Load a .e source file and execute it. Returns exit code."""
    source_path = Path(path)
    if not source_path.exists():
        print(f"E: I could not find the file '{path}'.")
        return 1
    if source_path.suffix != ".e":
        print(f"E: The file '{path}' doesn't end in .e. Are you sure?")
        return 1

    source = source_path.read_text(encoding="utf-8")
    return run_source(source, source_path.name, turtle_mode=turtle_mode)


def run_source(source: str, name: str = "<repl>", turtle_mode: str = "auto") -> int:
    """Run E source code through the full pipeline: lex -> parse -> execute.

    This is the heart of the interpreter. Wires together the components
    from src/ once they exist.
    """
    # Imports kept local to avoid circular issues during early phases.
    from src.lexer import Lexer
    from src.parser import Parser
    from src.interpreter import Interpreter
    from src.errors import EError, report_error

    try:
        tokens = Lexer(source, name).tokenize()
        ast = Parser(tokens, name).parse()
        Interpreter(name, turtle_mode=turtle_mode).run(ast)
        return 0
    except EError as err:
        report_error(err)
        return 1
    except KeyboardInterrupt:
        print("\nE: stopped.")
        return 130


def start_repl(turtle_mode: str = "auto") -> int:
    """Start the interactive E shell."""
    from src.interpreter import Interpreter
    from src.repl_helpers import (
        load_history, save_history_line, _input_with_history,
        cmd_help, cmd_vars, cmd_clear, bold, cyan, dim, red,
    )

    history = load_history()
    interp = Interpreter("<repl>", turtle_mode=turtle_mode)

    # Print greeting
    print(bold(cyan("Hi! Ready to code?")) + dim("  (type  help  for a quick reference)"))
    print()

    # Block-tracking keywords. We count these to decide if the user has
    # finished a multi-line statement. This is a simple heuristic — for
    # perfect behavior you'd re-lex/parse the buffer after each line.
    BLOCK_OPENERS = {"if", "while", "repeat", "for", "to"}
    BLOCK_CLOSER = "end"

    buffer: list = []

    def compute_depth(lines: list) -> int:
        """How many more 'end's do we need to close all open blocks?"""
        depth = 0
        for ln in lines:
            stripped = ln.strip()
            if not stripped or stripped.startswith("--"):
                continue
            # The first word on a non-empty line tells us if it opens a block.
            first = stripped.split()[0].lower()
            if first in BLOCK_OPENERS:
                depth += 1
            # Count 'end' occurrences on this line (rough).
            depth -= sum(1 for w in stripped.lower().split() if w == BLOCK_CLOSER)
        return depth

    while True:
        prompt = dim("... ") if buffer else cyan("e> ")
        try:
            line = _input_with_history(prompt, history)
        except (EOFError, KeyboardInterrupt):
            print()
            break

        stripped = line.strip()

        # Empty line: if no buffer, just continue; if buffer, ignore it
        if not stripped and not buffer:
            continue

        # Comment-only line: just skip
        if stripped.startswith("--"):
            continue

        # Exit keywords (case-insensitive) only when not in a block
        if not buffer and stripped.lower() in ("bye", "exit", "quit"):
            print(dim("E: bye!"))
            break

        # REPL commands (only when not in a block)
        if not buffer:
            low = stripped.lower()
            if low == "help":
                cmd_help()
                continue
            if low == "vars":
                cmd_vars(interp.global_env)
                continue
            if low == "clear":
                cmd_clear()
                continue

        # Add to history
        history.append(stripped)
        save_history_line(stripped)

        buffer.append(line)

        # Decide whether the buffered input is a complete statement.
        if compute_depth(buffer) > 0:
            continue  # read more lines

        full = "\n".join(buffer)
        buffer = []
        try:
            from src.lexer import Lexer
            from src.parser import Parser
            from src.errors import EError, report_error

            tokens = Lexer(full, "<repl>").tokenize()
            ast = Parser(tokens, "<repl>").parse()
            interp.run(ast)
        except EError as err:
            from src.errors import report_error
            report_error(err)
        except KeyboardInterrupt:
            print("\nE: stopped.")
            break

    return 0


def main() -> int:
    file_path, turtle_mode = _parse_args(sys.argv)
    if file_path is not None:
        return run_file(file_path, turtle_mode=turtle_mode)
    return start_repl(turtle_mode=turtle_mode)


if __name__ == "__main__":
    sys.exit(main())
