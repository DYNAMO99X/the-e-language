"""Bundle all src/*.py files into a single playground/e_bundle.py for Pyodide."""
import os
import sys

SRC_DIR = os.path.join(os.path.dirname(__file__), "src")
OUT = os.path.join(os.path.dirname(__file__), "playground", "e_bundle.py")

# Order matters: errors first, then tokens, lexer, ast_nodes, parser,
# environment, turtle_runtime, gui_runtime, interpreter, e (entry point).
FILES = [
    "errors.py",
    "tokens.py",
    "lexer.py",
    "ast_nodes.py",
    "parser.py",
    "environment.py",
    "turtle_runtime.py",
    "gui_runtime.py",
    "interpreter.py",
]

HEADER = '''\
"""E Language Interpreter -- Bundled for Pyodide (web playground).

This file combines all src/*.py modules into a single file so Pyodide
can load it without needing a file system.
"""
'''

sections = [HEADER]
for fname in FILES:
    path = os.path.join(SRC_DIR, fname)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    sections.append(f'\n# --- src/{fname} ---\n{content}\n')

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(sections))

print(f"Wrote {os.path.getsize(OUT):,} bytes to {OUT}")
