"""Token types and the Token dataclass for the E lexer.

A token is a single meaningful chunk of source code — a keyword, a number,
a string, a symbol, etc. The lexer scans source text and produces a flat
list of these tokens for the parser to consume.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from src.errors import SourceLocation


class TokenType(Enum):
    # --- Literals ---
    NUMBER = auto()        # 5, 3.14
    STRING = auto()        # "hello"
    IDENT = auto()         # variable / function names

    # --- Keywords ---
    LET = auto()           # let
    BE = auto()            # be
    SAY = auto()           # say
    ASK = auto()           # ask
    IF = auto()            # if
    THEN = auto()          # then
    ELSE = auto()          # else
    END = auto()           # end  (closes if / while / repeat / for / function)
    WHILE = auto()         # while
    REPEAT = auto()        # repeat
    TIMES = auto()         # times
    FOR = auto()           # for
    EACH = auto()          # each
    IN = auto()            # in
    TO = auto()            # to  (function definition: "to greet name")
    RETURN = auto()        # return
    TRUE = auto()          # true
    FALSE = auto()         # false
    NOTHING = auto()       # nothing
    AND = auto()           # and
    OR = auto()            # or
    NOT = auto()           # not

    # --- Comparison operators (as keywords / multi-word) ---
    IS = auto()            # is / is equal to
    IS_NOT_EQUAL = auto()  # is not equal to
    IS_GREATER = auto()    # is greater than
    IS_LESS = auto()       # is less than
    IS_GREATER_EQ = auto() # is greater than or equal to
    IS_LESS_EQ = auto()    # is less than or equal to

    # --- Math operators (as keywords) ---
    PLUS = auto()          # plus
    MINUS = auto()         # minus
    TIMES_KW = auto()      # times (used as math operator too)
    DIVIDED = auto()       # divided
    BY = auto()            # by
    MOD = auto()           # mod

    # --- Symbols / punctuation ---
    COMMA = auto()         # ,  (concatenation)
    LPAREN = auto()        # (
    RPAREN = auto()        # )
    LBRACKET = auto()      # [
    RBRACKET = auto()      # ]
    AT = auto()            # at    (list index: nums at 0)
    WITH = auto()          # with  (list add: nums with 6 added)
    ADDED = auto()         # added
    SIZE = auto()          # size of
    OF = auto()            # of    (used in "size of nums")

    # --- Turtle drawing ---
    TURTLE = auto()        # turtle  (the type/value in "let ada be turtle")
    MOVE = auto()          # move    ("move ada forward 50")
    MAKE = auto()          # make    ("make ada hide", "make ada draw circle 50")
    GOTO = auto()          # goto    ("make ada goto 50 right and 20 up")
    SET = auto()           # set     ("set ada pen color to 'red'")

    # --- Structural ---
    NEWLINE = auto()       # statement separator (optional in many places)
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: Any             # the textual value, or a parsed Python value for literals
    location: SourceLocation

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, L{self.location.line})"
