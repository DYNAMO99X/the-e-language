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

    # --- Math operators (as symbols) ---
    STAR = auto()          # *
    SLASH = auto()         # /

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

    # --- GUI windows ---
    WINDOW = auto()        # window  (the type/value in "let win be window")
    LABEL = auto()         # label   (widget type)
    BUTTON = auto()        # button  (widget type)
    TEXT_INPUT = auto()    # text input (widget type, multi-word)
    SHOW = auto()          # show    ("show win")
    HIDE = auto()          # hide    ("hide win")
    PLACE = auto()         # place   ("make win place btn at row 0 and column 0")
    WHEN = auto()          # when    ("make win do on_click when btn clicked")
    CLICKED = auto()       # clicked (event name)
    ROW = auto()           # row     (grid layout)
    COLUMN = auto()        # column  (grid layout)
    DO = auto()            # do      ("make win do on_click when btn clicked")
    TEXT_OF = auto()       # text of ("let val be text of name")
    # Web / JSON tokens
    STATUS_OF = auto()     # status of ("say status of resp")
    BODY_OF = auto()       # body of ("say body of resp")
    JSON_OF = auto()       # json of ("let data be json of resp")
    JSON_PARSE = auto()    # json parse ("let obj be json parse text")
    JSON_KEYS = auto()     # json keys ("let keys be json keys obj")
    JSON_VALUE = auto()    # json value ("let val be json value obj, key")
    TIMEOUT = auto()       # timeout keyword ("get url, timeout 5")

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
