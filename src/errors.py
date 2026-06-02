"""E-friendly error types and reporting.

All errors raised anywhere in the pipeline should be subclasses of EError
so the entry point can catch a single type and display a friendly message.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class SourceLocation:
    """A single position in a source file."""
    line: int       # 1-indexed
    column: int     # 1-indexed
    name: str       # filename or "<repl>"


class EError(Exception):
    """Base class for all E interpreter errors."""
    kind: str = "Error"

    def __init__(self, message: str, location: Optional[SourceLocation] = None):
        super().__init__(message)
        self.message = message
        self.location = location

    def format(self) -> str:
        loc = self.location
        if loc is None:
            return f"E {self.kind}: {self.message}"
        return f"E {self.kind} in {loc.name} on line {loc.line}: {self.message}"


class LexerError(EError):
    kind = "LexerError"


class ParseError(EError):
    kind = "ParseError"


class RuntimeError_(EError):
    kind = "RuntimeError"


class NameError_(EError):
    kind = "NameError"


class TypeError_(EError):
    kind = "TypeError"


def report_error(err: EError) -> None:
    """Print a friendly, English-style error message."""
    print(err.format())
