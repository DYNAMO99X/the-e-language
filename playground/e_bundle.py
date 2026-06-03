"""E Language Interpreter -- Bundled for Pyodide (web playground).

This file combines all src/*.py modules into a single file so Pyodide
can load it without needing a file system.
"""


# --- src/errors.py ---
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



# --- src/tokens.py ---
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



# --- src/lexer.py ---
"""Lexer for the E language.

Turns raw source text into a stream of tokens.

Handles:
- Whitespace and newlines
- Line comments starting with --
- String literals "..."
- Number literals (integers, decimals, and negative numbers at statement starts)
- Identifiers and all keywords
- Multi-word keywords (is greater than, is not equal to, divided by, ...)
- Symbols: , ( ) [ ] > < >= <= = == !=
"""

from __future__ import annotations
from typing import List, Optional

from src.tokens import Token, TokenType
from src.errors import LexerError, SourceLocation


# Multi-word phrases. Key = the FIRST word (lowercase). Value is an ordered
# list of (tail_words, token_type) pairs, longest tail first so the most
# specific phrase is preferred.
#
# Example: for "is", we try "is not equal to" before "is equal to" before
# "is greater than or equal to" before "is greater than".
_MULTI_WORD: dict = {
    "is": [
        (("not", "equal", "to"), TokenType.IS_NOT_EQUAL),
        (("equal", "to"), TokenType.IS),
        (("greater", "than", "or", "equal", "to"), TokenType.IS_GREATER_EQ),
        (("less", "than", "or", "equal", "to"), TokenType.IS_LESS_EQ),
        (("greater", "than"), TokenType.IS_GREATER),
        (("less", "than"), TokenType.IS_LESS),
    ],
    "divided": [
        (("by",), TokenType.DIVIDED),
    ],
    "text": [
        (("input",), TokenType.TEXT_INPUT),
        (("of",), TokenType.TEXT_OF),
    ],
}

# Single-word keywords. Every multi-word starter should ALSO be here, so the
# user can use the short form (e.g. just "is" for equality).
_KEYWORDS: dict = {
    "let": TokenType.LET,
    "be": TokenType.BE,
    "say": TokenType.SAY,
    "ask": TokenType.ASK,
    "if": TokenType.IF,
    "then": TokenType.THEN,
    "else": TokenType.ELSE,
    "end": TokenType.END,
    "while": TokenType.WHILE,
    "repeat": TokenType.REPEAT,
    "times": TokenType.TIMES,
    "for": TokenType.FOR,
    "each": TokenType.EACH,
    "in": TokenType.IN,
    "to": TokenType.TO,
    "return": TokenType.RETURN,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "nothing": TokenType.NOTHING,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
    "plus": TokenType.PLUS,
    "minus": TokenType.MINUS,
    "mod": TokenType.MOD,
    "is": TokenType.IS,
    "by": TokenType.BY,
    "at": TokenType.AT,
    "with": TokenType.WITH,
    "added": TokenType.ADDED,
    "size": TokenType.SIZE,
    "of": TokenType.OF,
    # Turtle drawing keywords
    "turtle": TokenType.TURTLE,
    "move": TokenType.MOVE,
    "make": TokenType.MAKE,
    "goto": TokenType.GOTO,
    "set": TokenType.SET,
    # GUI keywords
    "window": TokenType.WINDOW,
    "label": TokenType.LABEL,
    "button": TokenType.BUTTON,
    "show": TokenType.SHOW,
    "hide": TokenType.HIDE,
    "place": TokenType.PLACE,
    "when": TokenType.WHEN,
    "clicked": TokenType.CLICKED,
    "row": TokenType.ROW,
    "column": TokenType.COLUMN,
    "do": TokenType.DO,
}


class Lexer:
    def __init__(self, source: str, name: str = "<source>"):
        self.source = source
        self.name = name
        self.start = 0
        self.current = 0
        self.line = 1
        self.col = 1
        self.tokens: List[Token] = []

    # ---------- low-level helpers ----------

    def _loc(self, line: int, col: int) -> SourceLocation:
        return SourceLocation(line=line, column=col, name=self.name)

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _peek(self, offset: int = 0) -> str:
        idx = self.current + offset
        if idx >= len(self.source):
            return "\0"
        return self.source[idx]

    def _advance(self) -> str:
        ch = self.source[self.current]
        self.current += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _add(self, ttype: TokenType, value=None, loc: Optional[SourceLocation] = None) -> None:
        """Append a token. `value` defaults to the source text for this token."""
        if value is None:
            value = self.source[self.start:self.current]
        if loc is None:
            loc = self._loc(self.line, self.col)
        self.tokens.append(Token(ttype, value, loc))

    # ---------- lookahead for multi-word phrases ----------

    def _word_at(self, pos: int) -> tuple:
        """Read a single word (letters/digits/underscore) starting at pos.
        Returns (word, end_pos). The word does NOT cross newlines."""
        i = pos
        while i < len(self.source) and (self.source[i].isalnum() or self.source[i] == "_"):
            i += 1
        return self.source[pos:i], i

    def _try_multi_word(self, word_text: str, word_lower: str) -> bool:
        """If the current word is the start of a multi-word phrase and that
        phrase matches the upcoming text, consume the phrase, emit the
        appropriate token, and return True. Otherwise return False."""
        if word_lower not in _MULTI_WORD:
            return False

        for tail, ttype in _MULTI_WORD[word_lower]:
            probe = self.current
            # Require a single space (or tab) between the start word and the tail.
            if probe >= len(self.source) or self.source[probe] not in (" ", "\t"):
                continue
            probe += 1

            matched: List[str] = []
            ok = True
            for i, expected in enumerate(tail):
                w, end = self._word_at(probe)
                if w.lower() != expected:
                    ok = False
                    break
                matched.append(w)
                probe = end
                # Between tail words, require a single space (not the very last
                # one, which can be followed by anything that terminates a word).
                is_last = (i == len(tail) - 1)
                if not is_last:
                    if probe >= len(self.source) or self.source[probe] not in (" ", "\t"):
                        ok = False
                        break
                    probe += 1

            if not ok:
                continue

            # After the matched phrase, we must be at a word boundary (so we
            # don't accidentally eat the start of the next identifier).
            if probe < len(self.source):
                ch = self.source[probe]
                if ch.isalnum() or ch == "_":
                    continue

            # All checks passed. Consume the tail.
            while self.current < probe:
                self._advance()
            self._add(ttype, word_text + " " + " ".join(matched))
            return True

        return False

    # ---------- token scanners ----------

    def _string(self, quote_char: str) -> None:
        """Read a string literal delimited by `quote_char`.

        E supports three equivalent string delimiters: `"`, `'`, and `` ` ``.
        They all support the same escape sequences (`\n`, `\t`, `\\`, `\"`,
        `\'`, `` \` ``), and cross-quote escapes work too (e.g. `\'` inside
        `"..."`).
        """
        start_line = self.line
        start_col = self.col
        self._advance()  # opening quote
        value_chars: List[str] = []
        while not self._is_at_end() and self._peek() != quote_char:
            ch = self._advance()
            if ch == "\\" and not self._is_at_end():
                # Escape sequence: \n \t \" \' \` \\
                esc = self._advance()
                mapping = {
                    "n": "\n",
                    "t": "\t",
                    "\\": "\\",
                    '"': '"',
                    "'": "'",
                    "`": "`",
                }
                value_chars.append(mapping.get(esc, esc))
            else:
                value_chars.append(ch)
        if self._is_at_end():
            raise LexerError(
                f"I started reading a string on line {start_line} but never "
                f"found the closing {quote_char}.",
                self._loc(start_line, start_col),
            )
        self._advance()  # closing quote
        self._add(TokenType.STRING, "".join(value_chars),
                  loc=self._loc(start_line, start_col))

    def _number(self, is_negative: bool = False) -> None:
        if is_negative:
            self._advance()  # consume the leading '-'
        while not self._is_at_end() and self._peek().isdigit():
            self._advance()
        if self._peek() == "." and self._peek(1).isdigit():
            self._advance()  # dot
            while not self._is_at_end() and self._peek().isdigit():
                self._advance()
        text = self.source[self.start:self.current]
        try:
            value: float = float(text)
            if value.is_integer() and "." not in text:
                value = int(value)
        except ValueError:
            raise LexerError(
                f"I tried to read a number on line {self.line} but '{text}' is not a valid number.",
                self._loc(self.line, self.col),
            )
        self._add(TokenType.NUMBER, value)

    def _word(self) -> None:
        # read the whole identifier
        while not self._is_at_end() and (self._peek().isalnum() or self._peek() == "_"):
            self._advance()
        word_text = self.source[self.start:self.current]
        word_lower = word_text.lower()

        # Try to extend into a multi-word phrase first.
        if self._try_multi_word(word_text, word_lower):
            return

        # Single-word keyword?
        if word_lower in _KEYWORDS:
            self._add(_KEYWORDS[word_lower], word_text)
            return

        # Otherwise it's an identifier.
        self._add(TokenType.IDENT, word_text)

    def _is_value_position(self) -> bool:
        """True if the previous token is one that ENDS a value
        (a number, string, ident, etc.) — meaning a `-` here is binary minus."""
        if not self.tokens:
            return False
        prev_type = self.tokens[-1].type
        value_enders = {
            TokenType.NUMBER, TokenType.STRING, TokenType.IDENT,
            TokenType.TRUE, TokenType.FALSE, TokenType.NOTHING,
            TokenType.RPAREN, TokenType.RBRACKET,
        }
        return prev_type in value_enders

    # ---------- main loop ----------

    def tokenize(self) -> List[Token]:
        while not self._is_at_end():
            self.start = self.current
            c = self._peek()

            if c == " " or c == "\t" or c == "\r":
                self._advance()
            elif c == "\n":
                self._add(TokenType.NEWLINE, "\n")
                self._advance()
            elif c == "-" and self._peek(1) == "-":
                # line comment: skip to end of line
                while not self._is_at_end() and self._peek() != "\n":
                    self._advance()
            elif c == '"' or c == "'" or c == "`":
                self._string(c)
            elif c.isdigit():
                self._number()
            elif c == ">":
                self._advance()
                if self._peek() == "=":
                    self._advance()
                    self._add(TokenType.IS_GREATER_EQ, ">=")
                else:
                    self._add(TokenType.IS_GREATER, ">")
            elif c == "<":
                self._advance()
                if self._peek() == "=":
                    self._advance()
                    self._add(TokenType.IS_LESS_EQ, "<=")
                else:
                    self._add(TokenType.IS_LESS, "<")
            elif c == "=":
                self._advance()
                if self._peek() == "=":
                    self._advance()
                self._add(TokenType.IS, "=")
            elif c == "!":
                self._advance()
                if self._peek() == "=":
                    self._advance()
                    if self._peek() == "=":
                        self._advance()
                    self._add(TokenType.IS_NOT_EQUAL, "!=")
                else:
                    raise LexerError(
                        f"I ran into a character I don't understand: '!' "
                        f"(line {self.line}, column {self.col}).",
                        self._loc(self.line, self.col),
                    )
            elif c == "-" and self._peek(1).isdigit() and not self._is_value_position():
                # negative number literal (e.g. at start of statement, after
                # newline, after a keyword like 'be', or after a symbol like '(')
                self._number(is_negative=True)
            elif c == "-":
                # binary minus
                self._advance()
                self._add(TokenType.MINUS, "-")
            elif c.isalpha() or c == "_":
                self._word()
            elif c == ",":
                self._advance()
                self._add(TokenType.COMMA, ",")
            elif c == "(":
                self._advance()
                self._add(TokenType.LPAREN, "(")
            elif c == ")":
                self._advance()
                self._add(TokenType.RPAREN, ")")
            elif c == "[":
                self._advance()
                self._add(TokenType.LBRACKET, "[")
            elif c == "]":
                self._advance()
                self._add(TokenType.RBRACKET, "]")
            elif c == "+":
                self._advance()
                self._add(TokenType.PLUS, "+")
            elif c == "*":
                self._advance()
                self._add(TokenType.STAR, "*")
            elif c == "/":
                self._advance()
                self._add(TokenType.SLASH, "/")
            else:
                raise LexerError(
                    f"I ran into a character I don't understand: '{c}' "
                    f"(line {self.line}, column {self.col}).",
                    self._loc(self.line, self.col),
                )

        self.tokens.append(Token(TokenType.EOF, "", self._loc(self.line, self.col)))
        return self.tokens



# --- src/ast_nodes.py ---
"""Abstract Syntax Tree (AST) node definitions for E.

The parser turns tokens into a tree of these nodes, and the interpreter
walks the tree to actually run the program.

Each node has a `kind` (its type) and a `location` for error reporting.
Field names are descriptive so reading the tree is easy.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Any, Optional

from src.errors import SourceLocation


# --- Program / statements ---------------------------------------------------

@dataclass
class Program:
    statements: List["Statement"] = field(default_factory=list)
    location: Optional[SourceLocation] = None


class Statement:
    pass


@dataclass
class LetStatement(Statement):
    """`let x be 5`"""
    name: str
    value: "Expression"
    location: Optional[SourceLocation] = None


@dataclass
class SayStatement(Statement):
    """`say x` or `say "hi" , name`"""
    parts: List["Expression"]
    location: Optional[SourceLocation] = None


@dataclass
class AskStatement(Statement):
    """`ask "prompt: "`  (used inside `let name be ask ...`)"""
    prompt: "Expression"
    location: Optional[SourceLocation] = None


@dataclass
class IfStatement(Statement):
    """`if cond then ... else ... end` (else is a list of statements)"""
    condition: "Expression"
    then_branch: List[Statement]
    else_branch: Optional[List[Statement]] = None
    location: Optional[SourceLocation] = None


@dataclass
class WhileStatement(Statement):
    """`while cond ... end`"""
    condition: "Expression"
    body: List[Statement]
    location: Optional[SourceLocation] = None


@dataclass
class RepeatStatement(Statement):
    """`repeat 5 times ... end`"""
    count: "Expression"
    body: List[Statement]
    location: Optional[SourceLocation] = None


@dataclass
class ForEachStatement(Statement):
    """`for each item in items ... end`"""
    var_name: str
    iterable: "Expression"
    body: List[Statement]
    location: Optional[SourceLocation] = None


@dataclass
class FunctionDef(Statement):
    """`to greet name ... end`"""
    name: str
    params: List[str]
    body: List[Statement]
    location: Optional[SourceLocation] = None


@dataclass
class ReturnStatement(Statement):
    """`return x`"""
    value: Optional["Expression"]
    location: Optional[SourceLocation] = None


@dataclass
class ExpressionStatement(Statement):
    """A bare expression used as a statement (e.g. function call)."""
    expression: "Expression"
    location: Optional[SourceLocation] = None


# --- Expressions ------------------------------------------------------------

class Expression:
    pass


@dataclass
class NumberLiteral(Expression):
    value: float
    location: Optional[SourceLocation] = None


@dataclass
class StringLiteral(Expression):
    value: str
    location: Optional[SourceLocation] = None


@dataclass
class BoolLiteral(Expression):
    value: bool
    location: Optional[SourceLocation] = None


@dataclass
class NothingLiteral(Expression):
    location: Optional[SourceLocation] = None


@dataclass
class Identifier(Expression):
    name: str
    location: Optional[SourceLocation] = None


@dataclass
class ListLiteral(Expression):
    elements: List[Expression]
    location: Optional[SourceLocation] = None


@dataclass
class ConcatExpression(Expression):
    """`a , b , c` — joins left-to-right as strings."""
    parts: List[Expression]
    location: Optional[SourceLocation] = None


@dataclass
class BinaryOp(Expression):
    """Generic two-operand math or comparison op."""
    op: str           # 'plus', 'minus', 'times', 'divided by', 'mod',
                      # 'is', 'is not equal to', 'is greater than', etc.
    left: Expression
    right: Expression
    location: Optional[SourceLocation] = None


@dataclass
class UnaryOp(Expression):
    op: str           # 'not' / 'minus' (negation)
    operand: Expression
    location: Optional[SourceLocation] = None


@dataclass
class CallExpression(Expression):
    callee: str
    arguments: List[Expression]
    location: Optional[SourceLocation] = None


@dataclass
class IndexExpression(Expression):
    """`nums at 0`"""
    collection: Expression
    index: Expression
    location: Optional[SourceLocation] = None


@dataclass
class SizeExpression(Expression):
    """`size of nums`"""
    collection: Expression
    location: Optional[SourceLocation] = None


@dataclass
class WithAddedExpression(Expression):
    """`nums with 6 added`"""
    collection: Expression
    value: Expression
    location: Optional[SourceLocation] = None


# --- Turtle drawing ---------------------------------------------------------

@dataclass
class TurtleLiteral(Expression):
    """`turtle` — used on the RHS of `let ada be turtle` to create a new turtle."""
    location: Optional[SourceLocation] = None


@dataclass
class MoveStatement(Statement):
    """`move ada forward 50` / `move ada right 20` / etc.

    `direction` is one of: 'forward', 'backward', 'left', 'right'.
    `amount` is a numeric expression (in pixels for forward/backward,
    in degrees for left/right).
    """
    turtle_name: str
    direction: str       # 'forward' | 'backward' | 'left' | 'right'
    amount: Expression
    location: Optional[SourceLocation] = None


@dataclass
class MakeStatement(Statement):
    """`make ada hide` / `make ada show` / `make ada close pen` /
    `make ada open pen` / `make ada erase all` / `make ada restart` /
    `make ada go home` / `make ada draw circle 50` /
    `make ada draw dot 5` / `make ada speed 5` /
    `make ada go to 50 and 20` (raw goto) /
    `make ada goto 50 right and 20 up` (relative goto).

    `action` is the action keyword (string). For most actions `arg` is None;
    for actions that take a value (`draw circle`, `draw dot`, `speed`,
    `go to`), `arg` is a numeric expression.
    """
    turtle_name: str
    action: str          # 'hide' | 'show' | 'pen_up' | 'pen_down' | 'erase_all' |
                         # 'restart' | 'home' | 'draw_circle' | 'draw_dot' |
                         # 'speed' | 'go_to'
    arg: Optional[Expression] = None
    location: Optional[SourceLocation] = None


@dataclass
class GotoStatement(Statement):
    """`make ada goto 50 right and 20 up` — relative goto with direction words.

    `x_dir` and `y_dir` are 'right'/'left' and 'up'/'down' respectively.
    `x_amount` and `y_amount` are the magnitudes.
    """
    turtle_name: str
    x_amount: Expression
    x_dir: str           # 'right' | 'left'
    y_amount: Expression
    y_dir: str           # 'up' | 'down'
    location: Optional[SourceLocation] = None


@dataclass
class SetStatement(Statement):
    """`set ada pen color to 'red'` / `set ada pen size to '3'` /
    `set ada background to 'white'`.

    `property` is a string like 'pen color', 'pen size', or 'background'.
    """
    turtle_name: str
    property: str
    value: Expression
    location: Optional[SourceLocation] = None


@dataclass
class TurtlePropertyAccess(Expression):
    """`ada heading` / `ada x` / `ada y` — reads a property of a turtle.

    At parse time this looks like a function call (`ada` with arg `heading`),
    but at runtime the interpreter dispatches: if `ada` is a Turtle, this
    reads the property; if `ada` is a function, this is a regular call.
    """
    turtle_name: str
    property: str        # 'heading' | 'x' | 'y'
    location: Optional[SourceLocation] = None


# --- GUI windows ------------------------------------------------------------

@dataclass
class WindowLiteral(Expression):
    """`window` — used on the RHS of `let win be window` to create a new window."""
    location: Optional[SourceLocation] = None


@dataclass
class WidgetCreate(Statement):
    """`let btn be button "Click Me" on win`
    `let lbl be label "Hello" on win`
    `let name be text input "Your name" on win`

    `widget_type` is 'label', 'button', or 'text input'.
    `args` holds the initial text (may be empty).
    `parent` is the window expression.
    """
    var_name: str
    widget_type: str         # 'label' | 'button' | 'text input'
    args: List[Expression]
    parent: Expression
    location: Optional[SourceLocation] = None


@dataclass
class SetProperty(Statement):
    """`set win title to "My App"` / `set greet text to "Hello"` /
    `set btn color to "blue"` / `set greet font size to 16`.

    `prop` is the property name as a string (e.g. 'title', 'text', 'color',
    'font size').
    """
    obj: Expression
    prop: str
    value: Expression
    location: Optional[SourceLocation] = None


@dataclass
class PlaceWidget(Statement):
    """`make win place btn at row 0 and column 1`"""
    window: Expression
    widget: Expression
    row: Expression
    column: Expression
    location: Optional[SourceLocation] = None


@dataclass
class HandleEvent(Statement):
    """`make win do on_click when btn clicked`"""
    window: Expression
    handler: str             # function name
    widget: Expression
    event: str               # 'clicked'
    location: Optional[SourceLocation] = None


@dataclass
class ShowWindow(Statement):
    """`show win`"""
    window: Expression
    location: Optional[SourceLocation] = None


@dataclass
class HideWindow(Statement):
    """`hide win`"""
    window: Expression
    location: Optional[SourceLocation] = None


@dataclass
class TextOf(Expression):
    """`text of name` — reads the current text value of a widget."""
    widget: Expression
    location: Optional[SourceLocation] = None



# --- src/parser.py ---
"""Parser for the E language.

Turns a flat list of tokens into an Abstract Syntax Tree (AST).

Expression grammar (lowest to highest precedence):
    expression  := concat
    concat      := or ("," or)*
    or          := and ("or" and)*
    and         := unary ("and" unary)*
    unary       := "not" unary | comparison
    comparison  := additive (comp_op additive)?
    additive    := multiplicative (("plus" | "minus") multiplicative)*
    multiplicative := unary_minus (("times" | "divided" "by" | "mod") unary_minus)*
    unary_minus := "-" unary_minus | postfix
    postfix     := primary ("at" expression | "with" expression "added")*
    primary     := "size" "of" primary
                 | NUMBER | STRING | TRUE | FALSE | NOTHING
                 | IDENT ( expression ("," expression)* )?   -- function call
                 | IDENT                                          -- identifier
                 | "ask" expression                                -- input
                 | "[" (expression ("," expression)*)? "]"
                 | "(" expression ")"

Statement grammar:
    program     := (statement NEWLINE?)*
    statement   := "let" IDENT "be" expression
                 | "say" expression
                 | "if" expression "then" block ("else" block)? "end"
                 | "while" expression block "end"
                 | "repeat" expression "times" block "end"
                 | "for" "each" IDENT "in" expression block "end"
                 | "to" IDENT (IDENT)* block "end"
                 | "return" expression?
                 | expression
"""

from __future__ import annotations
from typing import List, Optional, Set

from src.tokens import Token, TokenType
from src.ast_nodes import (
    Program, Statement, LetStatement, SayStatement, IfStatement,
    WhileStatement, RepeatStatement, ForEachStatement, FunctionDef,
    ReturnStatement, ExpressionStatement,
    NumberLiteral, StringLiteral, BoolLiteral, NothingLiteral, Identifier,
    ListLiteral, ConcatExpression, BinaryOp, UnaryOp, CallExpression,
    IndexExpression, SizeExpression, WithAddedExpression,
    TurtleLiteral, MoveStatement, MakeStatement, GotoStatement, SetStatement,
    WindowLiteral, WidgetCreate, SetProperty, PlaceWidget, HandleEvent,
    ShowWindow, HideWindow, TextOf,
)
from src.errors import ParseError, SourceLocation


# Tokens that START an expression. Used to decide whether an IDENT is
# followed by arguments (i.e. a function call). Note: MINUS is NOT here
# because after an identifier, `-` is a binary subtraction, not unary minus.
# Unary minus is still handled correctly via parse_unary() at the start of
# an expression.
_EXPR_START: Set[TokenType] = {
    TokenType.NUMBER, TokenType.STRING, TokenType.IDENT,
    TokenType.TRUE, TokenType.FALSE, TokenType.NOTHING,
    TokenType.LPAREN, TokenType.LBRACKET, TokenType.NOT,
    TokenType.SIZE,  # 'size of X'
    TokenType.TEXT_OF,  # 'text of widget'
}

# Tokens that END a block (no statements after these in the current block).
_BLOCK_END: Set[TokenType] = {TokenType.END, TokenType.ELSE, TokenType.EOF}

# Tokens that begin a new statement (so the previous statement is done).
_STMT_START: Set[TokenType] = {
    TokenType.LET, TokenType.SAY, TokenType.IF, TokenType.WHILE,
    TokenType.REPEAT, TokenType.FOR, TokenType.TO, TokenType.RETURN,
    TokenType.MOVE, TokenType.MAKE, TokenType.SET,
    TokenType.SHOW, TokenType.HIDE,
}


class Parser:
    def __init__(self, tokens: List[Token], name: str = "<source>"):
        self.tokens = tokens
        self.name = name
        self.pos = 0

    # ---------- helpers ----------

    def _peek(self, offset: int = 0) -> Token:
        idx = self.pos + offset
        if idx >= len(self.tokens):
            return self.tokens[-1]  # EOF
        return self.tokens[idx]

    def _at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def _check(self, ttype: TokenType) -> bool:
        return self._peek().type == ttype

    def _match(self, *ttype: TokenType) -> Optional[Token]:
        if self._peek().type in ttype:
            return self._advance()
        return None

    def _expect(self, ttype: TokenType, message: str) -> Token:
        tok = self._peek()
        if tok.type != ttype:
            raise ParseError(
                f"{message} (I found '{tok.value}' on line {tok.location.line}, "
                f"column {tok.location.column} instead.)",
                tok.location,
            )
        return self._advance()

    def _skip_newlines(self) -> None:
        while self._check(TokenType.NEWLINE):
            self._advance()

    def _error(self, message: str) -> ParseError:
        tok = self._peek()
        return ParseError(
            f"{message} (line {tok.location.line}, column {tok.location.column}, "
            f"near '{tok.value}')",
            tok.location,
        )

    # ---------- top-level ----------

    def parse(self) -> Program:
        statements: List[Statement] = []
        self._skip_newlines()
        while not self._at_end():
            stmt = self._parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self._skip_newlines()
        return Program(statements=statements,
                       location=SourceLocation(1, 1, self.name))

    # ---------- statements ----------

    def _parse_statement(self) -> Optional[Statement]:
        tok = self._peek()
        if tok.type == TokenType.LET:
            return self._parse_let()
        if tok.type == TokenType.SAY:
            return self._parse_say()
        if tok.type == TokenType.IF:
            return self._parse_if()
        if tok.type == TokenType.WHILE:
            return self._parse_while()
        if tok.type == TokenType.REPEAT:
            return self._parse_repeat()
        if tok.type == TokenType.FOR:
            return self._parse_for()
        if tok.type == TokenType.TO:
            return self._parse_function_def()
        if tok.type == TokenType.RETURN:
            return self._parse_return()
        if tok.type == TokenType.MOVE:
            return self._parse_move()
        if tok.type == TokenType.MAKE:
            return self._parse_make()
        if tok.type == TokenType.SET:
            return self._parse_set()
        if tok.type == TokenType.SHOW:
            return self._parse_show()
        if tok.type == TokenType.HIDE:
            return self._parse_hide()

        # Bare expression statement (e.g. a function call).
        expr = self._parse_expression()
        if expr is None:
            return None
        return ExpressionStatement(expression=expr, location=expr.location)

    def _parse_let(self) -> LetStatement:
        let_tok = self._advance()  # LET
        name_tok = self._expect(TokenType.IDENT, "After 'let' I expected a name for the variable")
        self._expect(TokenType.BE, "After the variable name I expected 'be'")

        # `let win be window`
        if self._check(TokenType.WINDOW):
            self._advance()
            return LetStatement(
                name=name_tok.value,
                value=WindowLiteral(location=let_tok.location),
                location=let_tok.location,
            )

        # `let btn be button "Click Me" on win`
        # `let lbl be label "Hello" on win`
        # `let name be text input "Your name" on win`
        if self._check(TokenType.BUTTON):
            return self._parse_widget_create(let_tok, name_tok, "button")
        if self._check(TokenType.LABEL):
            return self._parse_widget_create(let_tok, name_tok, "label")
        if self._check(TokenType.TEXT_INPUT):
            return self._parse_widget_create(let_tok, name_tok, "text input")

        value = self._parse_expression()
        if value is None:
            raise self._error("After 'be' I expected a value for the variable")
        return LetStatement(
            name=name_tok.value,
            value=value,
            location=let_tok.location,
        )

    def _parse_widget_create(self, let_tok, name_tok, widget_type) -> LetStatement:
        """`let btn be button "Click Me" on win`"""
        self._advance()  # consume widget type token
        # Parse optional initial text argument
        args = []
        if self._peek().type in (TokenType.STRING, TokenType.NUMBER,
                                  TokenType.IDENT, TokenType.LPAREN):
            # Don't consume 'on' as an argument
            if not (self._peek().type == TokenType.IDENT and
                    str(self._peek().value).lower() == "on"):
                arg = self._parse_expression()
                if arg is not None:
                    args.append(arg)
        # Expect `on <window>`
        on_tok = self._expect(TokenType.IDENT, f"After '{widget_type}' I expected 'on' and a window name")
        if str(on_tok.value).lower() != "on":
            raise self._error(f"After the widget text I expected 'on'")
        parent = self._parse_expression()
        if parent is None:
            raise self._error(f"After 'on' I expected the window name")
        return LetStatement(
            name=name_tok.value,
            value=WidgetCreate(
                var_name=name_tok.value,
                widget_type=widget_type,
                args=args,
                parent=parent,
                location=let_tok.location,
            ),
            location=let_tok.location,
        )

    def _parse_say(self) -> SayStatement:
        say_tok = self._advance()  # SAY
        # say takes one expression (which can contain commas for concat)
        expr = self._parse_expression()
        if expr is None:
            raise self._error("After 'say' I expected something to say")
        return SayStatement(parts=[expr], location=say_tok.location)

    def _parse_if(self) -> IfStatement:
        if_tok = self._advance()  # IF
        condition = self._parse_expression()
        if condition is None:
            raise self._error("After 'if' I expected a condition")
        # `then` is optional and may appear on the same line or a later one.
        self._skip_newlines()
        if self._check(TokenType.THEN):
            self._advance()
            self._skip_newlines()
        then_branch = self._parse_block(_BLOCK_END)
        else_branch: Optional[List[Statement]] = None
        consumed_end = False  # set if the else was an "else if" form
        if self._check(TokenType.ELSE):
            self._advance()  # ELSE
            if self._check(TokenType.IF):
                # "else if" form: the inner if consumes its own 'end', so
                # the outer if does NOT need another one. The chain can
                # keep going via further "else if"s, all sharing a single 'end'.
                else_branch = [self._parse_if()]
                consumed_end = True
            else:
                self._skip_newlines()
                else_branch = self._parse_block(_BLOCK_END)
        if not consumed_end:
            self._expect(TokenType.END, "I was looking for 'end' to finish the if")
        return IfStatement(
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch,
            location=if_tok.location,
        )

    def _parse_while(self) -> WhileStatement:
        w_tok = self._advance()  # WHILE
        condition = self._parse_expression()
        if condition is None:
            raise self._error("After 'while' I expected a condition")
        self._skip_newlines()
        body = self._parse_block(_BLOCK_END)
        self._expect(TokenType.END, "I was looking for 'end' to finish the while loop")
        return WhileStatement(condition=condition, body=body, location=w_tok.location)

    def _parse_repeat(self) -> RepeatStatement:
        r_tok = self._advance()  # REPEAT
        # Use _parse_primary (not _parse_expression) so that the word 'times'
        # is NOT consumed as the multiplication operator. If you need arithmetic,
        # wrap it in parens: `repeat (5 plus 3) times`.
        count = self._parse_primary()
        if count is None:
            raise self._error("After 'repeat' I expected a number")
        # Allow `times` on the same line OR the next non-empty line.
        self._skip_newlines()
        self._expect(TokenType.TIMES, "After the number I expected 'times'")
        self._skip_newlines()
        body = self._parse_block(_BLOCK_END)
        self._expect(TokenType.END, "I was looking for 'end' to finish the repeat loop")
        return RepeatStatement(count=count, body=body, location=r_tok.location)

    def _parse_for(self) -> ForEachStatement:
        f_tok = self._advance()  # FOR
        self._expect(TokenType.EACH, "After 'for' I expected 'each'")
        var_tok = self._expect(TokenType.IDENT, "After 'for each' I expected a variable name")
        self._expect(TokenType.IN, "After the variable name I expected 'in'")
        # Use _parse_or (not _parse_expression) so commas inside list literals
        # work correctly: `for each x in [1, 2, 3]`.
        iterable = self._parse_or()
        if iterable is None:
            raise self._error("After 'in' I expected something to loop over")
        self._skip_newlines()
        body = self._parse_block(_BLOCK_END)
        self._expect(TokenType.END, "I was looking for 'end' to finish the for loop")
        return ForEachStatement(
            var_name=var_tok.value,
            iterable=iterable,
            body=body,
            location=f_tok.location,
        )

    def _parse_function_def(self) -> FunctionDef:
        to_tok = self._advance()  # TO
        name_tok = self._expect(TokenType.IDENT, "After 'to' I expected a function name")
        params: List[str] = []
        # Parameters are identifiers, until we hit a newline.
        while self._peek().type == TokenType.IDENT:
            params.append(self._advance().value)
        if not params:
            raise self._error(
                f"The function '{name_tok.value}' has no parameters. "
                f"Functions need at least one name between 'to' and the body."
            )
        self._skip_newlines()
        body = self._parse_block(_BLOCK_END)
        self._expect(TokenType.END, "I was looking for 'end' to finish the function")
        return FunctionDef(
            name=name_tok.value,
            params=params,
            body=body,
            location=to_tok.location,
        )

    def _parse_return(self) -> ReturnStatement:
        r_tok = self._advance()  # RETURN
        # Return may have an expression or not (just `return` for nothing).
        if (self._peek().type in _BLOCK_END
                or self._peek().type == TokenType.NEWLINE
                or self._peek().type in _STMT_START):
            return ReturnStatement(value=None, location=r_tok.location)
        value = self._parse_expression()
        return ReturnStatement(value=value, location=r_tok.location)

    def _parse_block(self, end_tokens: Set[TokenType]) -> List[Statement]:
        """Parse statements until we hit a token in end_tokens or EOF."""
        stmts: List[Statement] = []
        while not self._at_end() and self._peek().type not in end_tokens:
            stmt = self._parse_statement()
            if stmt is not None:
                stmts.append(stmt)
            self._skip_newlines()
        return stmts

    # ---------- expressions (precedence climbing) ----------

    def _parse_expression(self) -> Optional[object]:
        """Top of the expression chain. Comma is the lowest operator."""
        left = self._parse_or()
        if left is None:
            return None
        if self._check(TokenType.COMMA):
            parts = [left]
            while self._check(TokenType.COMMA):
                self._advance()
                nxt = self._parse_or()
                if nxt is None:
                    raise self._error("After ',' I expected another value")
                parts.append(nxt)
            return ConcatExpression(parts=parts, location=left.location)
        return left

    def _parse_or(self) -> Optional[object]:
        left = self._parse_and()
        while left is not None and self._check(TokenType.OR):
            self._advance()
            right = self._parse_and()
            if right is None:
                raise self._error("After 'or' I expected a value")
            left = BinaryOp(op="or", left=left, right=right,
                            location=left.location)
        return left

    def _parse_and(self) -> Optional[object]:
        left = self._parse_unary_logic()
        while left is not None and self._check(TokenType.AND):
            self._advance()
            right = self._parse_unary_logic()
            if right is None:
                raise self._error("After 'and' I expected a value")
            left = BinaryOp(op="and", left=left, right=right,
                            location=left.location)
        return left

    def _parse_unary_logic(self) -> Optional[object]:
        if self._check(TokenType.NOT):
            op_tok = self._advance()
            operand = self._parse_unary_logic()
            if operand is None:
                raise self._error("After 'not' I expected a value")
            return UnaryOp(op="not", operand=operand, location=op_tok.location)
        return self._parse_comparison()

    def _parse_comparison(self) -> Optional[object]:
        left = self._parse_additive()
        if left is None:
            return None
        comp_map = {
            TokenType.IS: "is",
            TokenType.IS_NOT_EQUAL: "is not equal to",
            TokenType.IS_GREATER: "is greater than",
            TokenType.IS_LESS: "is less than",
            TokenType.IS_GREATER_EQ: "is greater than or equal to",
            TokenType.IS_LESS_EQ: "is less than or equal to",
        }
        if self._peek().type in comp_map:
            op_tok = self._advance()
            right = self._parse_additive()
            if right is None:
                raise self._error(
                    f"After '{op_tok.value}' I expected a value to compare with"
                )
            return BinaryOp(op=comp_map[op_tok.type], left=left, right=right,
                            location=op_tok.location)
        return left

    def _parse_additive(self) -> Optional[object]:
        left = self._parse_multiplicative()
        while left is not None and self._peek().type in (TokenType.PLUS, TokenType.MINUS):
            op_tok = self._advance()
            right = self._parse_multiplicative()
            if right is None:
                raise self._error(f"After '{op_tok.value}' I expected a value")
            op = "plus" if op_tok.type == TokenType.PLUS else "minus"
            left = BinaryOp(op=op, left=left, right=right,
                            location=left.location)
        return left

    def _parse_multiplicative(self) -> Optional[object]:
        left = self._parse_unary()
        while left is not None and self._peek().type in (
                TokenType.TIMES, TokenType.STAR, TokenType.DIVIDED,
                TokenType.SLASH, TokenType.MOD):
            op_tok = self._advance()
            right = self._parse_unary()
            if right is None:
                raise self._error(f"After '{op_tok.value}' I expected a value")
            if op_tok.type in (TokenType.TIMES, TokenType.STAR):
                op = "times"
            elif op_tok.type in (TokenType.DIVIDED, TokenType.SLASH):
                op = "divided by"
            else:
                op = "mod"
            left = BinaryOp(op=op, left=left, right=right,
                            location=left.location)
        return left

    def _parse_unary(self) -> Optional[object]:
        # Unary minus (only when MINUS isn't already part of a negative number,
        # which the lexer handled; here we handle bare MINUS like `-x`).
        if self._check(TokenType.MINUS):
            op_tok = self._advance()
            operand = self._parse_unary()
            if operand is None:
                raise self._error("After '-' I expected a value")
            return UnaryOp(op="minus", operand=operand, location=op_tok.location)
        return self._parse_postfix()

    def _parse_postfix(self) -> Optional[object]:
        expr = self._parse_size_of_or_primary()
        while expr is not None and self._check(TokenType.AT):
            self._advance()
            index = self._parse_unary()
            if index is None:
                raise self._error("After 'at' I expected an index value")
            expr = IndexExpression(collection=expr, index=index, location=expr.location)
        if expr is not None and self._check(TokenType.WITH):
            self._advance()
            value = self._parse_unary()
            if value is None:
                raise self._error("After 'with' I expected a value to add")
            self._expect(TokenType.ADDED, "After the value I expected 'added'")
            expr = WithAddedExpression(collection=expr, value=value, location=expr.location)
        return expr

    def _parse_size_of_or_primary(self) -> Optional[object]:
        if self._check(TokenType.SIZE):
            op_tok = self._advance()
            self._expect(TokenType.OF, "After 'size' I expected 'of'")
            operand = self._parse_size_of_or_primary()  # right-associative
            if operand is None:
                raise self._error("After 'size of' I expected a value")
            return SizeExpression(collection=operand, location=op_tok.location)
        if self._check(TokenType.TEXT_OF):
            op_tok = self._advance()
            operand = self._parse_size_of_or_primary()  # right-associative
            if operand is None:
                raise self._error("After 'text of' I expected a widget name")
            return TextOf(widget=operand, location=op_tok.location)
        return self._parse_primary()

    def _parse_primary(self) -> Optional[object]:
        tok = self._peek()

        if tok.type == TokenType.NUMBER:
            self._advance()
            return NumberLiteral(value=tok.value, location=tok.location)
        if tok.type == TokenType.STRING:
            self._advance()
            return StringLiteral(value=tok.value, location=tok.location)
        if tok.type == TokenType.TRUE:
            self._advance()
            return BoolLiteral(value=True, location=tok.location)
        if tok.type == TokenType.FALSE:
            self._advance()
            return BoolLiteral(value=False, location=tok.location)
        if tok.type == TokenType.NOTHING:
            self._advance()
            return NothingLiteral(location=tok.location)
        if tok.type == TokenType.TURTLE:
            self._advance()
            return TurtleLiteral(location=tok.location)
        if tok.type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_expression()
            if expr is None:
                raise self._error("Inside '(' I expected a value")
            self._expect(TokenType.RPAREN, "I was looking for ')'")
            return expr
        if tok.type == TokenType.LBRACKET:
            return self._parse_list_literal()
        if tok.type == TokenType.IDENT:
            return self._parse_ident_or_call()
        if tok.type == TokenType.ASK:
            return self._parse_ask()

        return None

    def _parse_ask(self) -> object:
        ask_tok = self._advance()  # ASK
        prompt = self._parse_expression()
        if prompt is None:
            raise self._error("After 'ask' I expected a prompt string")
        return CallExpression(callee="ask", arguments=[prompt], location=ask_tok.location)

    def _parse_ident_or_call(self) -> object:
        name_tok = self._advance()  # IDENT
        # Look ahead: if the next token starts an expression, this is a call.
        if self._peek().type in _EXPR_START:
            # Function call args are SINGLE VALUES (possibly with postfix).
            # Use a restricted parser so the call doesn't greedily eat operators
            # that belong to the surrounding expression. For complex args,
            # wrap them in parens: `add (3 plus 4), 5`.
            args: List[object] = [self._parse_call_arg()]
            while self._check(TokenType.COMMA):
                self._advance()
                nxt = self._parse_call_arg()
                if nxt is None:
                    raise self._error("After ',' in a function call I expected a value")
                args.append(nxt)
            return CallExpression(callee=name_tok.value, arguments=args,
                                  location=name_tok.location)
        return Identifier(name=name_tok.value, location=name_tok.location)

    def _parse_call_arg(self) -> Optional[object]:
        """Parse a single function-call argument.

        A call arg is a primary (literal, identifier, parenthesized expr,
        list literal) possibly followed by postfix `at` / `with ... added`.
        It does NOT include binary operators, comparisons, or boolean logic —
        those belong to the surrounding expression. Use parens for complex args.
        """
        expr = self._parse_primary()
        if expr is None:
            return None
        # Postfix `at`
        while self._check(TokenType.AT):
            self._advance()
            index = self._parse_call_arg()  # index is also a single value
            if index is None:
                raise self._error("After 'at' I expected an index value")
            expr = IndexExpression(collection=expr, index=index, location=expr.location)
        # Postfix `with ... added`
        if self._check(TokenType.WITH):
            self._advance()
            value = self._parse_call_arg()
            if value is None:
                raise self._error("After 'with' I expected a value to add")
            self._expect(TokenType.ADDED, "After the value I expected 'added'")
            expr = WithAddedExpression(collection=expr, value=value, location=expr.location)
        return expr

    def _parse_list_literal(self) -> object:
        lb_tok = self._advance()  # [
        elements: List[object] = []
        self._skip_newlines()  # allow multi-line lists
        if not self._check(TokenType.RBRACKET):
            # Use _parse_or so commas SEPARATE elements (not build concat).
            first = self._parse_or()
            if first is None:
                raise self._error("Inside '[' I expected a value")
            elements.append(first)
            while self._check(TokenType.COMMA):
                self._advance()
                self._skip_newlines()
                if self._check(TokenType.RBRACKET):
                    break  # trailing comma is OK
                nxt = self._parse_or()
                if nxt is None:
                    raise self._error("Inside '[' I expected a value after ','")
                elements.append(nxt)
        self._skip_newlines()
        self._expect(TokenType.RBRACKET, "I was looking for ']' to close the list")
        return ListLiteral(elements=elements, location=lb_tok.location)

    # ---------- turtle statements ----------

    def _expect_ident(self, message: str) -> str:
        tok = self._peek()
        if tok.type != TokenType.IDENT:
            raise self._error(message)
        self._advance()
        return str(tok.value)

    def _parse_move(self) -> MoveStatement:
        """`move ada forward 50` / `move ada right 20` / etc."""
        move_tok = self._advance()  # MOVE
        name = self._expect_ident("After 'move' I expected a turtle's name")
        dir_tok = self._peek()
        direction: Optional[str] = None
        if dir_tok.type == TokenType.IDENT:
            word = str(dir_tok.value).lower()
            if word in ("forward", "backward", "left", "right"):
                direction = word
                self._advance()
        if direction is None:
            raise self._error(
                "After 'move <turtle>' I expected 'forward', 'backward', "
                "'left', or 'right'"
            )
        amount = self._parse_expression()
        if amount is None:
            raise self._error(f"After 'move <turtle> {direction}' I expected a number")
        return MoveStatement(
            turtle_name=name, direction=direction, amount=amount,
            location=move_tok.location,
        )

    def _parse_make(self) -> Statement:
        """`make ada <action>` — many forms, see docs/turtle.md.
        Also handles GUI: `make win place btn at row 0 and column 0`
        and `make win do on_click when btn clicked`.
        """
        make_tok = self._advance()  # MAKE
        name = self._expect_ident("After 'make' I expected a name")

        # `make win do on_click when btn clicked`
        if self._check(TokenType.DO):
            return self._parse_handle_event(make_tok, name)

        # `make win place btn at row 0 and column 0`
        if self._check(TokenType.PLACE):
            return self._parse_place_widget(make_tok, name)

        # `make ada goto 50 right and 20 up`
        if self._check(TokenType.GOTO):
            return self._parse_make_goto_relative(make_tok, name)

        # Everything else starts with an IDENT, HIDE, or SHOW.
        nxt = self._peek()
        # Handle `make ada hide` / `make ada show` when hide/show are keywords
        if nxt.type in (TokenType.HIDE, TokenType.SHOW):
            word = nxt.type.name.lower()
            self._advance()
            return MakeStatement(
                turtle_name=name, action=word, arg=None,
                location=make_tok.location,
            )
        if nxt.type != TokenType.IDENT:
            raise self._error(
                f"After 'make {name}' I expected an action "
                f"(hide, show, close, open, erase, restart, home, draw, speed, go, goto)"
            )
        word = str(nxt.value).lower()
        self._advance()  # consume the action word

        # `make ada go home`
        if word == "go" and self._check(TokenType.IDENT) and \
                str(self._peek().value).lower() == "home":
            self._advance()
            return MakeStatement(
                turtle_name=name, action="home", arg=None,
                location=make_tok.location,
            )

        # `make ada go to X and Y`
        if word == "go" and self._check(TokenType.TO):
            self._advance()  # consume 'to'
            # Use _parse_additive (not _parse_expression) so the `and` between
            # the two coordinates is not greedily consumed as logical AND.
            x = self._parse_additive()
            if x is None:
                raise self._error("After 'make X go to' I expected a number for x")
            self._expect(TokenType.AND, "After the x value I expected 'and'")
            y = self._parse_additive()
            if y is None:
                raise self._error("After 'and' I expected a number for y")
            return MakeStatement(
                turtle_name=name, action="go_to",
                arg=ListLiteral(elements=[x, y], location=x.location),
                location=make_tok.location,
            )

        # `make ada close pen` / `make ada open pen`
        if word == "close" and self._check(TokenType.IDENT) and \
                str(self._peek().value).lower() == "pen":
            self._advance()
            return MakeStatement(
                turtle_name=name, action="pen_up", arg=None,
                location=make_tok.location,
            )
        if word == "open" and self._check(TokenType.IDENT) and \
                str(self._peek().value).lower() == "pen":
            self._advance()
            return MakeStatement(
                turtle_name=name, action="pen_down", arg=None,
                location=make_tok.location,
            )

        # `make ada erase all`
        if word == "erase" and self._check(TokenType.IDENT) and \
                str(self._peek().value).lower() == "all":
            self._advance()
            return MakeStatement(
                turtle_name=name, action="erase_all", arg=None,
                location=make_tok.location,
            )

        # `make ada draw circle 50` / `make ada draw dot 5`
        if word == "draw":
            shape_tok = self._peek()
            if shape_tok.type != TokenType.IDENT:
                raise self._error(
                    "After 'make X draw' I expected 'circle' or 'dot'"
                )
            shape = str(shape_tok.value).lower()
            if shape not in ("circle", "dot"):
                raise self._error(
                    f"I don't know how to draw a '{shape}'. "
                    f"Try 'circle' or 'dot'."
                )
            self._advance()
            arg = self._parse_expression()
            if arg is None:
                raise self._error(
                    f"After 'make X draw {shape}' I expected a number for the size"
                )
            return MakeStatement(
                turtle_name=name, action=f"draw_{shape}", arg=arg,
                location=make_tok.location,
            )

        # No-arg actions
        if word in ("hide", "show", "restart"):
            return MakeStatement(
                turtle_name=name, action=word, arg=None,
                location=make_tok.location,
            )

        # `make ada speed 5`
        if word == "speed":
            arg = self._parse_expression()
            if arg is None:
                raise self._error("After 'make X speed' I expected a number from 0 to 10")
            return MakeStatement(
                turtle_name=name, action="speed", arg=arg,
                location=make_tok.location,
            )

        raise self._error(
            f"I don't know the action '{word}' for a turtle. "
            f"Try: hide, show, close pen, open pen, erase all, restart, "
            f"go home, go to X and Y, draw circle, draw dot, speed, or goto."
        )

    def _parse_place_widget(self, make_tok, window_name: str) -> PlaceWidget:
        """`make win place btn at row 0 and column 0`"""
        self._advance()  # consume PLACE
        widget_name = self._expect_ident("After 'place' I expected a widget name")
        widget = Identifier(name=widget_name, location=make_tok.location)
        self._expect(TokenType.AT, "After the widget name I expected 'at'")
        self._expect(TokenType.ROW, "After 'at' I expected 'row'")
        row = self._parse_primary()
        if row is None:
            raise self._error("After 'row' I expected a number")
        self._expect(TokenType.AND, "After the row I expected 'and'")
        self._expect(TokenType.COLUMN, "After 'and' I expected 'column'")
        col = self._parse_primary()
        if col is None:
            raise self._error("After 'column' I expected a number")
        return PlaceWidget(
            window=Identifier(name=window_name, location=make_tok.location),
            widget=widget,
            row=row,
            column=col,
            location=make_tok.location,
        )

    def _parse_handle_event(self, make_tok, window_name: str) -> HandleEvent:
        """`make win do on_click when btn clicked`"""
        self._advance()  # consume DO
        handler_tok = self._expect(TokenType.IDENT, "After 'do' I expected a function name")
        self._expect(TokenType.WHEN, "After the function name I expected 'when'")
        widget_name = self._expect_ident("After 'when' I expected a widget name")
        widget = Identifier(name=widget_name, location=make_tok.location)
        self._expect(TokenType.CLICKED, "After the widget name I expected 'clicked'")
        return HandleEvent(
            window=Identifier(name=window_name, location=make_tok.location),
            handler=handler_tok.value,
            widget=widget,
            event="clicked",
            location=make_tok.location,
        )

    def _parse_make_goto_relative(self, make_tok, name: str) -> GotoStatement:
        """`make ada goto 50 right and 20 up`"""
        self._advance()  # consume GOTO
        # Use _parse_additive (not _parse_expression) so the `and` between
        # the two coordinates is not greedily consumed as a logical AND.
        x_amount = self._parse_additive()
        if x_amount is None:
            raise self._error("After 'goto' I expected a number for the x amount")
        x_dir_tok = self._peek()
        if x_dir_tok.type != TokenType.IDENT or \
                str(x_dir_tok.value).lower() not in ("right", "left"):
            raise self._error(
                "After the x amount I expected 'right' or 'left'"
            )
        x_dir = str(x_dir_tok.value).lower()
        self._advance()
        self._expect(TokenType.AND, "After the x direction I expected 'and'")
        y_amount = self._parse_additive()
        if y_amount is None:
            raise self._error("After 'and' I expected a number for the y amount")
        y_dir_tok = self._peek()
        if y_dir_tok.type != TokenType.IDENT or \
                str(y_dir_tok.value).lower() not in ("up", "down"):
            raise self._error(
                "After the y amount I expected 'up' or 'down'"
            )
        y_dir = str(y_dir_tok.value).lower()
        self._advance()
        return GotoStatement(
            turtle_name=name,
            x_amount=x_amount, x_dir=x_dir,
            y_amount=y_amount, y_dir=y_dir,
            location=make_tok.location,
        )

    def _parse_set(self) -> Statement:
        """`set ada pen color to 'red'` / `set win title to "My App"` /
        `set greet text to "Hello"` / `set btn color to "blue"`."""
        set_tok = self._advance()  # SET
        name = self._expect_ident("After 'set' I expected a name")
        # Look for property name (multi-word supported for GUI).
        property_name = self._parse_set_property(name)
        self._expect(TokenType.TO, f"After the property name I expected 'to'")
        value = self._parse_expression()
        if value is None:
            raise self._error(
                f"After 'set {name} {property_name} to' I expected a value"
            )
        return SetStatement(
            turtle_name=name, property=property_name, value=value,
            location=set_tok.location,
        )

    def _parse_set_property(self, obj_name: str) -> str:
        """Read the property name after `set <obj>`.

        Supports `pen color`, `pen size` (turtles), or GUI properties like
        `title`, `text`, `color`, `font size`.
        """
        first = self._peek()
        if first.type != TokenType.IDENT:
            raise self._error(
                f"After 'set {obj_name}' I expected a property name "
                f"(like 'title', 'text', 'color', or 'font size')"
            )
        word = str(first.value).lower()
        if word == "pen":
            self._advance()
            second = self._peek()
            second_text = str(second.value).lower() if second.value is not None else ""
            if second_text not in ("color", "size"):
                raise self._error(
                    f"After 'set {obj_name} pen' I expected 'color' or 'size'"
                )
            self._advance()
            return f"pen {second_text}"
        self._advance()
        # Check for multi-word properties: `font size`
        if word == "font" and (self._check(TokenType.IDENT) or self._check(TokenType.SIZE)):
            second = self._peek()
            second_text = str(second.value).lower() if second.value is not None else ""
            if second_text == "size":
                self._advance()
                return "font size"
        return word

    # --- GUI statements ---

    def _parse_show(self) -> ShowWindow:
        """`show win`"""
        show_tok = self._advance()  # SHOW
        expr = self._parse_expression()
        if expr is None:
            raise self._error("After 'show' I expected a window name")
        return ShowWindow(window=expr, location=show_tok.location)

    def _parse_hide(self) -> HideWindow:
        """`hide win`"""
        hide_tok = self._advance()  # HIDE
        expr = self._parse_expression()
        if expr is None:
            raise self._error("After 'hide' I expected a window name")
        return HideWindow(window=expr, location=hide_tok.location)



# --- src/environment.py ---
"""Scoped environment (variable + function storage) for the interpreter.

Implemented in Phase 5.
"""

from __future__ import annotations
from typing import Any, Optional, Callable, List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.ast_nodes import FunctionDef


class Environment:
    def __init__(self, parent: Optional["Environment"] = None):
        self.parent = parent
        self.variables: dict = {}
        self.functions: dict = {}

    def define(self, name: str, value: Any) -> None:
        self.variables[name] = value

    def get(self, name: str) -> Any:
        env = self
        while env is not None:
            if name in env.variables:
                return env.variables[name]
            env = env.parent
        raise KeyError(name)

    def set(self, name: str, value: Any) -> None:
        env = self
        while env is not None:
            if name in env.variables:
                env.variables[name] = value
                return
            env = env.parent
        raise KeyError(name)

    def has(self, name: str) -> bool:
        env = self
        while env is not None:
            if name in env.variables:
                return True
            env = env.parent
        return False

    def define_function(self, name: str, func: "FunctionDef") -> None:
        self.functions[name] = func

    def get_function(self, name: str) -> Optional["FunctionDef"]:
        env = self
        while env is not None:
            if name in env.functions:
                return env.functions[name]
            env = env.parent
        return None

    def child(self) -> "Environment":
        return Environment(parent=self)



# --- src/turtle_runtime.py ---
"""Turtle runtime for the E language.

Provides a `Turtle` class that wraps Python's built-in `turtle` module,
plus a `TurtleManager` that tracks multiple named turtles within a single
E program.

Supports two modes:

* `window` — opens a real tkinter window and draws visually.
* `text`   — headless. No window is opened; instead, every command is
             appended to a per-turtle command log. Useful for tests and
             for running on a machine with no display (e.g. CI).

The mode is selected at construction time. When `auto` is requested, the
runtime tries to open a window; if tkinter fails for any reason, it
falls back to text mode silently.
"""

from __future__ import annotations
import math
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------- one turtle ----------

class Turtle:
    """A single named turtle. Maintains its own state.

    In window mode, every state-changing method also forwards to Python's
    `turtle.Turtle` so a window appears. In text mode, state is tracked
    locally and commands are appended to `self.log`.
    """

    def __init__(self, name: str, mode: str):
        self.name = name
        self.mode = mode                # 'window' | 'text'
        self.log: List[str] = []

        # State
        self.x: float = 0.0
        self.y: float = 0.0
        self.heading: float = 0.0       # degrees; 0 = right (east)
        self.pen_down: bool = True
        self.pen_color: str = "black"
        self.pen_size: int = 1
        self.background: str = "white"
        self.visible: bool = True
        self.speed: int = 3             # 0 = fastest, 1-10 = slow to medium

        # Underlying Python turtle (only in window mode)
        self._t: Optional[object] = None
        if self.mode == "window":
            try:
                import turtle as _py_turtle
                self._t = _py_turtle.Turtle()
                self._t.speed(self.speed)
            except Exception:
                # tkinter failed — fall back to text mode for this turtle
                self.mode = "text"
                self._t = None

    # ----- low-level helpers -----

    def _log(self, msg: str) -> None:
        if self.mode == "text":
            self.log.append(f">> {msg}")

    def _to_radians(self) -> float:
        return math.radians(self.heading)

    # ----- movement -----

    def forward(self, n: float) -> None:
        if self.pen_down and self._t is not None:
            self._t.forward(n)         # type: ignore[union-attr]
        rad = self._to_radians()
        self.x += n * math.cos(rad)
        self.y += n * math.sin(rad)
        self._log(f"forward {n}")

    def backward(self, n: float) -> None:
        if self.pen_down and self._t is not None:
            self._t.backward(n)        # type: ignore[union-attr]
        rad = self._to_radians()
        self.x -= n * math.cos(rad)
        self.y -= n * math.sin(rad)
        self._log(f"backward {n}")

    def left(self, n: float) -> None:
        if self._t is not None:
            self._t.left(n)             # type: ignore[union-attr]
        self.heading = (self.heading + n) % 360
        self._log(f"left {n}")

    def right(self, n: float) -> None:
        if self._t is not None:
            self._t.right(n)            # type: ignore[union-attr]
        self.heading = (self.heading - n) % 360
        self._log(f"right {n}")

    # ----- cursor visibility -----

    def hide(self) -> None:
        self.visible = False
        if self._t is not None:
            self._t.hideturtle()        # type: ignore[union-attr]
        self._log("hide")

    def show(self) -> None:
        self.visible = True
        if self._t is not None:
            self._t.showturtle()        # type: ignore[union-attr]
        self._log("show")

    # ----- pen state -----
    # Methods are named raise_pen/lower_pen so they don't collide with the
    # self.pen_down boolean attribute.

    def raise_pen(self) -> None:
        self.pen_down = False
        if self._t is not None:
            self._t.penup()             # type: ignore[union-attr]
        self._log("pen_up")

    def lower_pen(self) -> None:
        self.pen_down = True
        if self._t is not None:
            self._t.pendown()           # type: ignore[union-attr]
        self._log("pen_down")

    # ----- clearing / resetting -----

    def clear(self) -> None:
        if self._t is not None:
            self._t.clear()             # type: ignore[union-attr]
        self.log.clear()
        self._log("erase_all")

    def home(self) -> None:
        if self._t is not None:
            self._t.home()              # type: ignore[union-attr]
        self.x = 0.0
        self.y = 0.0
        self.heading = 0.0
        self._log("home")

    def reset(self) -> None:
        """Factory reset: clear + home + restore all defaults."""
        if self._t is not None:
            self._t.reset()             # type: ignore[union-attr]
        self.x = 0.0
        self.y = 0.0
        self.heading = 0.0
        self.pen_down = True
        self.pen_color = "black"
        self.pen_size = 1
        self.background = "white"
        self.visible = True
        self.speed = 3
        self.log.clear()
        self._log("restart")

    # ----- shape drawing -----

    def circle(self, r: float) -> None:
        if self._t is not None:
            self._t.circle(r)           # type: ignore[union-attr]
        # Approximate: 36 sample points (full circle) and update position
        # based on the heading. Python's turtle.circle() with the default
        # extent=360 leaves the turtle at the start; we mirror that.
        self._log(f"draw_circle {r}")

    def dot(self, size: float) -> None:
        if self._t is not None:
            self._t.dot(int(size))      # type: ignore[union-attr]
        self._log(f"draw_dot {size}")

    # ----- positioning -----

    def goto_relative(self, x_amount: float, x_dir: str,
                      y_amount: float, y_dir: str) -> None:
        dx = x_amount if x_dir == "right" else -x_amount
        dy = y_amount if y_dir == "up"    else -y_amount
        target_x = self.x + dx
        target_y = self.y + dy
        if self._t is not None:
            self._t.goto(target_x, target_y)  # type: ignore[union-attr]
        self.x = target_x
        self.y = target_y
        self._log(f"goto {x_amount} {x_dir} and {y_amount} {y_dir}")

    def goto_absolute(self, x: float, y: float) -> None:
        if self._t is not None:
            self._t.goto(x, y)          # type: ignore[union-attr]
        self.x = x
        self.y = y
        self._log(f"go_to {x} and {y}")

    # ----- speed -----

    def set_speed(self, n: int) -> None:
        self.speed = max(0, min(10, int(n)))
        if self._t is not None:
            self._t.speed(self.speed)   # type: ignore[union-attr]
        self._log(f"speed {self.speed}")

    # ----- properties (for `set`) -----

    def set_pen_color(self, color: str) -> None:
        self.pen_color = str(color)
        if self._t is not None:
            self._t.pencolor(self.pen_color)  # type: ignore[union-attr]
        self._log(f"pen_color {self.pen_color}")

    def set_pen_size(self, n: int) -> None:
        self.pen_size = max(1, int(n))
        if self._t is not None:
            self._t.pensize(self.pen_size)     # type: ignore[union-attr]
        self._log(f"pen_size {self.pen_size}")

    def set_background(self, color: str) -> None:
        self.background = str(color)
        if self._t is not None:
            try:
                import turtle as _py_turtle
                _py_turtle.bgcolor(self.background)  # type: ignore[union-attr]
            except Exception:
                pass
        self._log(f"background {self.background}")

    # ----- finalization -----

    def close(self) -> None:
        """Release the underlying turtle (if any). Safe to call multiple times."""
        if self._t is not None:
            try:
                self._t.hideturtle()    # type: ignore[union-attr]
            except Exception:
                pass


# ---------- the manager ----------

class TurtleManager:
    """Owns all turtles for one E program run.

    Mode can be 'auto' (try to open a window, fall back to text), 'window'
    (force a window), or 'text' (headless, no window).
    """

    def __init__(self, requested_mode: str = "auto"):
        if requested_mode not in ("auto", "window", "text"):
            raise ValueError(
                f"turtle mode must be 'auto', 'window', or 'text', "
                f"got {requested_mode!r}"
            )
        self.requested_mode = requested_mode
        self.turtles: Dict[str, Turtle] = {}
        self._resolved_mode: Optional[str] = None
        self._init_error: Optional[str] = None

    def _resolve_mode(self) -> str:
        if self._resolved_mode is not None:
            return self._resolved_mode
        if self.requested_mode == "text":
            self._resolved_mode = "text"
            return self._resolved_mode
        # Try window mode
        try:
            import tkinter                      # noqa: F401
            self._resolved_mode = "window"
        except Exception as e:
            self._init_error = str(e)
            self._resolved_mode = "text"
        return self._resolved_mode

    def create(self, name: str) -> Turtle:
        if name in self.turtles:
            raise RuntimeError(
                f"You already made a turtle called '{name}'. "
                f"Give it a different name."
            )
        mode = self._resolve_mode()
        t = Turtle(name, mode)
        self.turtles[name] = t
        return t

    def get(self, name: str) -> Turtle:
        if name not in self.turtles:
            raise RuntimeError(
                f"I don't know a turtle called '{name}'. "
                f"Did you forget to write `let {name} be turtle` first?"
            )
        return self.turtles[name]

    def close_all(self) -> None:
        for t in self.turtles.values():
            t.close()
        # If we opened any window, try to clean it up. Importing inside
        # the function keeps the import optional.
        if self._resolved_mode == "window":
            try:
                import turtle as _py_turtle
                _py_turtle.bye()
            except Exception:
                # We're probably not in the main thread; just let the
                # window be. Python's atexit will clean up.
                pass



# --- src/gui_runtime.py ---
"""GUI window runtime for the E language.

Follows the same pattern as turtle_runtime.py:
- WindowManager owns all GUI windows/widgets for one E program run.
- Text-mode fallback: every GUI command is logged to a list so tests
  can verify them without needing a display.
- Window mode: creates real tkinter widgets.

Usage from the interpreter:
    wm = GuiManager(requested_mode="auto")
    wm.create_window("win")
    wm.create_widget("button", "btn", "win", "Click Me")
    wm.set_property("win", "title", "My App")
    wm.place_widget("win", "btn", 0, 0)
    wm.handle_event("win", "on_click", "btn", "clicked")
    wm.show_window("win")
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any


class _Widget:
    """Internal representation of a GUI widget."""

    def __init__(self, widget_type: str, name: str, parent: str, text: str = ""):
        self.widget_type = widget_type
        self.name = name
        self.parent = parent
        self.text = text
        self.properties: Dict[str, Any] = {}
        self._tk_widget = None  # real tkinter widget in window mode

    def __repr__(self) -> str:
        return f"<{self.widget_type} '{self.name}' text='{self.text}'>"


class _Window:
    """Internal representation of a GUI window."""

    def __init__(self, name: str):
        self.name = name
        self.properties: Dict[str, Any] = {"title": "E Program", "width": 400, "height": 300}
        self.widgets: Dict[str, _Widget] = {}
        self._tk_root = None  # real tkinter root in window mode
        self._tk_frames: Dict[str, Any] = {}  # grid frame storage

    def __repr__(self) -> str:
        return f"<window '{self.name}' widgets={len(self.widgets)}>"


class GuiManager:
    """Manages GUI windows and widgets for an E program run.

    Follows the same dual-mode pattern as TurtleManager:
    - 'window' mode: creates real tkinter widgets
    - 'text' mode: logs commands for testing
    - 'auto' mode: tries window, falls back to text
    """

    def __init__(self, requested_mode: str = "auto"):
        self._mode = self._resolve_mode(requested_mode)
        self._windows: Dict[str, _Window] = {}
        self._widgets: Dict[str, _Widget] = {}  # flat lookup by name
        self._log: List[str] = []
        self._event_handlers: Dict[str, str] = {}  # "win.btn.clicked" -> handler_name
        self._tk_initialized = False

    # --- mode resolution ---

    def _resolve_mode(self, requested: str) -> str:
        if requested == "window":
            try:
                import tkinter
                return "window"
            except ImportError:
                return "text"
        if requested == "text":
            return "text"
        # auto: try window, fall back to text
        try:
            import tkinter
            return "window"
        except ImportError:
            return "text"

    @property
    def mode(self) -> str:
        return self._mode

    # --- window operations ---

    def create_window(self, name: str) -> str:
        """Create a new window. Returns the window name."""
        if name in self._windows:
            self._log.append(f"restart_window {name}")
            return name
        self._windows[name] = _Window(name)
        self._log.append(f"create_window {name}")

        if self._mode == "window" and not self._tk_initialized:
            try:
                import tkinter as tk
                self._tk_initialized = True
            except ImportError:
                pass

        return name

    def set_property(self, obj_name: str, prop: str, value: Any) -> None:
        """Set a property on a window or widget."""
        # Check windows first
        if obj_name in self._windows:
            win = self._windows[obj_name]
            win.properties[prop] = value
            self._log.append(f"set_property {obj_name} {prop} {value}")

            # Apply to real tkinter widget if in window mode
            if self._mode == "window" and win._tk_root:
                if prop == "title":
                    win._tk_root.title(str(value))
                elif prop == "width":
                    win._tk_root.geometry(f"{int(value)}x{win.properties.get('height', 300)}")
                elif prop == "height":
                    win._tk_root.geometry(f"{win.properties.get('width', 400)}x{int(value)}")
            return

        # Check widgets
        if obj_name in self._widgets:
            w = self._widgets[obj_name]
            w.properties[prop] = value
            # Update text in both modes
            if prop == "text":
                w.text = str(value)
            self._log.append(f"set_property {obj_name} {prop} {value}")

            # Apply to real tkinter widget if in window mode
            if self._mode == "window" and w._tk_widget:
                if prop == "text":
                    try:
                        w._tk_widget.config(text=str(value))
                    except Exception:
                        pass
                elif prop == "color":
                    try:
                        w._tk_widget.config(fg=str(value))
                    except Exception:
                        pass
                elif prop == "bg":
                    try:
                        w._tk_widget.config(bg=str(value))
                    except Exception:
                        pass
                elif prop == "font size":
                    try:
                        w._tk_widget.config(font=("", int(value)))
                    except Exception:
                        pass
            return

        raise ValueError(f"I don't know an object called '{obj_name}'")

    def get_property(self, obj_name: str, prop: str) -> Any:
        """Read a property from a window or widget."""
        if obj_name in self._windows:
            return self._windows[obj_name].properties.get(prop)
        if obj_name in self._widgets:
            w = self._widgets[obj_name]
            if prop == "text":
                return w.text
            return w.properties.get(prop)
        raise ValueError(f"I don't know an object called '{obj_name}'")

    # --- widget operations ---

    def create_widget(self, widget_type: str, name: str, parent: str, text: str = "") -> str:
        """Create a new widget on a window. Returns the widget name."""
        if parent not in self._windows:
            raise ValueError(
                f"I can't create a '{widget_type}' on '{parent}' — "
                f"'{parent}' is not a window."
            )
        self._widgets[name] = _Widget(widget_type, name, parent, text)
        self._log.append(f"create_widget {widget_type} {name} on {parent} text={text}")

        # Create real tkinter widget if in window mode
        if self._mode == "window" and parent in self._windows:
            win = self._windows[parent]
            if win._tk_root:
                try:
                    import tkinter as tk
                    if widget_type == "label":
                        w = tk.Label(win._tk_root, text=text)
                    elif widget_type == "button":
                        w = tk.Button(win._tk_root, text=text)
                    elif widget_type == "text input":
                        w = tk.Entry(win._tk_root)
                        w.insert(0, text)
                    else:
                        w = tk.Label(win._tk_root, text=text)
                    self._widgets[name]._tk_widget = w
                except Exception:
                    pass

        self._log.append(f"create_widget {widget_type} {name} on {parent} text='{text}'")
        return name

    def place_widget(self, window_name: str, widget_name: str, row: int, column: int) -> None:
        """Place a widget in a grid layout."""
        self._log.append(f"place_widget {widget_name} at row {row} column {column}")

        if self._mode == "window":
            win = self._windows.get(window_name)
            if win and win._tk_root:
                w = self._widgets.get(widget_name)
                if w and w._tk_widget:
                    try:
                        w._tk_widget.grid(row=row, column=column, padx=5, pady=5, sticky="ew")
                    except Exception:
                        pass

    def handle_event(self, window_name: str, handler_name: str, widget_name: str, event: str) -> None:
        """Bind an event handler to a widget."""
        key = f"{window_name}.{widget_name}.{event}"
        self._event_handlers[key] = handler_name
        self._log.append(f"handle_event {handler_name} when {widget_name} {event}")

    def show_window(self, window_name: str) -> None:
        """Show the window and start the event loop (window mode) or log it (text mode)."""
        self._log.append(f"show_window {window_name}")

        if self._mode == "window":
            win = self._windows.get(window_name)
            if win and win._tk_root:
                try:
                    win._tk_root.mainloop()
                except Exception:
                    pass

    def hide_window(self, window_name: str) -> None:
        """Hide the window."""
        self._log.append(f"hide_window {window_name}")

        if self._mode == "window":
            win = self._windows.get(window_name)
            if win and win._tk_root:
                try:
                    win._tk_root.withdraw()
                except Exception:
                    pass

    def get_text_of(self, widget_name: str) -> str:
        """Read the current text value of a widget."""
        if widget_name in self._widgets:
            w = self._widgets[widget_name]
            # In window mode, read from the real tkinter widget
            if self._mode == "window" and w._tk_widget:
                try:
                    return w._tk_widget.get()
                except Exception:
                    try:
                        return w._tk_widget.cget("text")
                    except Exception:
                        pass
            return w.text
        self._log.append(f"get_text_of {widget_name}")
        return ""

    # --- logging (for text mode tests) ---

    def get_log(self) -> List[str]:
        """Return the command log for text-mode testing."""
        return list(self._log)



# --- src/interpreter.py ---
"""Interpreter for the E language.

Walks the AST produced by the parser and actually runs the program.
"""

from __future__ import annotations
from typing import List, Optional, Callable, Any

from src.ast_nodes import (
    Program, Statement, LetStatement, SayStatement, IfStatement,
    WhileStatement, RepeatStatement, ForEachStatement, FunctionDef,
    ReturnStatement, ExpressionStatement,
    NumberLiteral, StringLiteral, BoolLiteral, NothingLiteral, Identifier,
    ListLiteral, ConcatExpression, BinaryOp, UnaryOp, CallExpression,
    IndexExpression, SizeExpression, WithAddedExpression,
    TurtleLiteral, MoveStatement, MakeStatement, GotoStatement, SetStatement,
    WindowLiteral, WidgetCreate, SetProperty, PlaceWidget, HandleEvent,
    ShowWindow, HideWindow, TextOf,
)
from src.environment import Environment
from src.errors import RuntimeError_, NameError_, TypeError_, SourceLocation
from src.turtle_runtime import TurtleManager
from src.gui_runtime import GuiManager


# Internal control-flow signals. These are caught by the interpreter
# at function boundaries.
class _ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class _BreakSignal(Exception):
    pass


class _ContinueSignal(Exception):
    pass


# Sentinel returned by TurtleLiteral evaluation. _exec_let looks for this
# to know it should create a fresh turtle bound to the let-name.
class _turtle_factory_marker:
    """Singleton sentinel: tells `_exec_let` to create a new turtle."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self):
        return "<turtle-factory>"


# Sentinel returned by WindowLiteral evaluation. _exec_let looks for this
# to know it should create a fresh window bound to the let-name.
class _window_factory_marker:
    """Singleton sentinel: tells `_exec_let` to create a new window."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self):
        return "<window-factory>"


# Type name helpers for friendly error messages.
def _typename(v: Any) -> str:
    if isinstance(v, bool):
        return "true/false"
    if isinstance(v, (int, float)):
        return "number"
    if isinstance(v, str):
        return "text"
    if isinstance(v, list):
        return "list"
    if v is None:
        return "nothing"
    return type(v).__name__


def _to_text(v: Any) -> str:
    """Convert any E value to a readable text form (for `,` concat and `say`)."""
    if v is None:
        return "nothing"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, list):
        return "[" + ", ".join(_to_text(x) for x in v) + "]"
    return str(v)


def _to_number(v: Any) -> Any:
    """Convert to a number if possible; raise a friendly error otherwise."""
    if isinstance(v, bool):
        raise TypeError_(
            f"I can't do math with {_typename(v)} ({_to_text(v)}). Use a number."
        )
    if isinstance(v, (int, float)):
        return v
    if isinstance(v, str):
        try:
            n = float(v)
            if n.is_integer():
                return int(n)
            return n
        except ValueError:
            raise TypeError_(
                f"I can't turn the text \"{v}\" into a number."
            )
    raise TypeError_(
        f"I can't do math with {_typename(v)} ({_to_text(v)}). Use a number."
    )


def _to_bool(v: Any) -> bool:
    """E's truthiness: false/nothing are false; everything else is true."""
    if v is None or v is False:
        return False
    return True


class Interpreter:
    def __init__(self, name: str = "<source>", turtle_mode: str = "auto"):
        self.name = name
        self.global_env = Environment()
        self.output_buffer: List[str] = []
        self.turtles = TurtleManager(requested_mode=turtle_mode)
        self.gui = GuiManager(requested_mode=turtle_mode)
        self._install_builtins()

    # ---------- public ----------

    def run(self, program: Program) -> None:
        """Execute a parsed program."""
        self._exec_stmts(program.statements, self.global_env)

    def run_string(self, source: str) -> None:
        """Lex, parse, and run a source string (used by the REPL)."""
        from src.lexer import Lexer
        from src.parser import Parser
        toks = Lexer(source, "<repl>").tokenize()
        prog = Parser(toks, "<repl>").parse()
        self.run(prog)

    # ---------- built-ins ----------

    def _install_builtins(self) -> None:
        """Register built-in functions in the global environment.

        Built-ins are plain Python functions that take pre-evaluated args.
        The interpreter validates argument counts at the call site.
        """
        self._builtins: dict = {
            "ask": self._builtin_ask,
            "number": self._builtin_number,
            "text": self._builtin_text,
            "random": self._builtin_random,
            "uppercase": self._builtin_uppercase,
            "lowercase": self._builtin_lowercase,
        }
        for name, fn in self._builtins.items():
            self.global_env.define_function(name, fn)  # type: ignore[arg-type]

    def _builtin_ask(self, args, loc):
        if len(args) != 1:
            raise TypeError_(
                f"`ask` takes exactly 1 argument (a prompt), but I got {len(args)}.",
                loc,
            )
        prompt = _to_text(args[0])
        try:
            return input(prompt)
        except EOFError:
            return ""

    def _builtin_number(self, args, loc):
        if len(args) != 1:
            raise TypeError_(
                f"`number` takes exactly 1 argument, but I got {len(args)}.",
                loc,
            )
        return _to_number(args[0])

    def _builtin_text(self, args, loc):
        if len(args) != 1:
            raise TypeError_(
                f"`text` takes exactly 1 argument, but I got {len(args)}.",
                loc,
            )
        return _to_text(args[0])

    def _builtin_random(self, args, loc):
        if len(args) != 2:
            raise TypeError_(
                f"`random` takes 2 arguments (low, high), but I got {len(args)}.",
                loc,
            )
        lo = _to_number(args[0])
        hi = _to_number(args[1])
        if lo > hi:
            lo, hi = hi, lo
        import random as _r
        if isinstance(lo, int) and isinstance(hi, int):
            return _r.randint(int(lo), int(hi))
        return _r.uniform(lo, hi)

    def _builtin_uppercase(self, args, loc):
        if len(args) != 1:
            raise TypeError_(
                f"`uppercase` takes exactly 1 argument, but I got {len(args)}.",
                loc,
            )
        if not isinstance(args[0], str):
            raise TypeError_(
                f"`uppercase` needs text, but I got {_typename(args[0])}.",
                loc,
            )
        return args[0].upper()

    def _builtin_lowercase(self, args, loc):
        if len(args) != 1:
            raise TypeError_(
                f"`lowercase` takes exactly 1 argument, but I got {len(args)}.",
                loc,
            )
        if not isinstance(args[0], str):
            raise TypeError_(
                f"`lowercase` needs text, but I got {_typename(args[0])}.",
                loc,
            )
        return args[0].lower()

    # ---------- statements ----------

    def _exec_stmts(self, stmts: List[Statement], env: Environment) -> None:
        for s in stmts:
            self._exec(s, env)

    def _exec(self, stmt: Statement, env: Environment) -> None:
        method = self._DISPATCH.get(type(stmt))
        if method is None:
            raise RuntimeError_(
                f"I don't know how to run a {type(stmt).__name__}.",
                getattr(stmt, "location", None),
            )
        method(self, stmt, env)

    def _exec_let(self, stmt: LetStatement, env: Environment) -> None:
        # `let ada be turtle` — create a new turtle and bind it to the name.
        if isinstance(stmt.value, TurtleLiteral):
            t = self.turtles.create(stmt.name)
            env.define(stmt.name, t)
            return
        # `let win be window` — create a new window and bind it to the name.
        if isinstance(stmt.value, WindowLiteral):
            self.gui.create_window(stmt.name)
            env.define(stmt.name, stmt.name)
            return
        # `let btn be button "Click Me" on win` — create a widget.
        if isinstance(stmt.value, WidgetCreate):
            self._exec_widget_create(stmt.value, env)
            env.define(stmt.name, stmt.name)
            return
        value = self._eval(stmt.value, env)
        env.define(stmt.name, value)

    def _exec_say(self, stmt: SayStatement, env: Environment) -> None:
        # Each `parts` element is a full expression (which may contain a
        # ConcatExpression inside). We render each one as text.
        for part in stmt.parts:
            value = self._eval(part, env)
            text = _to_text(value)
            self.output_buffer.append(text)
            print(text)

    def _exec_if(self, stmt: IfStatement, env: Environment) -> None:
        if _to_bool(self._eval(stmt.condition, env)):
            self._exec_stmts(stmt.then_branch, env)
        elif stmt.else_branch is not None:
            self._exec_stmts(stmt.else_branch, env)

    def _exec_while(self, stmt: WhileStatement, env: Environment) -> None:
        while _to_bool(self._eval(stmt.condition, env)):
            try:
                self._exec_stmts(stmt.body, env)
            except _ContinueSignal:
                continue
            except _BreakSignal:
                break

    def _exec_repeat(self, stmt: RepeatStatement, env: Environment) -> None:
        count = _to_number(self._eval(stmt.count, env))
        count = int(count)
        if count < 0:
            count = 0
        for _ in range(count):
            try:
                self._exec_stmts(stmt.body, env)
            except _ContinueSignal:
                continue
            except _BreakSignal:
                break

    def _exec_for_each(self, stmt: ForEachStatement, env: Environment) -> None:
        iterable = self._eval(stmt.iterable, env)
        if not isinstance(iterable, list):
            raise TypeError_(
                f"I can only loop over a list, but I got {_typename(iterable)} "
                f"({_to_text(iterable)}).",
                stmt.iterable.location,
            )
        for item in iterable:
            loop_env = env.child()
            loop_env.define(stmt.var_name, item)
            try:
                self._exec_stmts(stmt.body, loop_env)
            except _ContinueSignal:
                continue
            except _BreakSignal:
                break

    def _exec_function_def(self, stmt: FunctionDef, env: Environment) -> None:
        env.define_function(stmt.name, stmt)

    def _exec_return(self, stmt: ReturnStatement, env: Environment) -> None:
        value = self._eval(stmt.value, env) if stmt.value is not None else None
        raise _ReturnSignal(value)

    def _exec_expr_stmt(self, stmt: ExpressionStatement, env: Environment) -> None:
        # A bare expression as a statement — useful for calling functions
        # whose return value we ignore.
        self._eval(stmt.expression, env)

    # ----- turtle statements -----

    def _exec_move(self, stmt: MoveStatement, env: Environment) -> None:
        t = self.turtles.get(stmt.turtle_name)
        amount = _to_number(self._eval(stmt.amount, env))
        if stmt.direction == "forward":
            t.forward(amount)
        elif stmt.direction == "backward":
            t.backward(amount)
        elif stmt.direction == "left":
            t.left(amount)
        elif stmt.direction == "right":
            t.right(amount)
        else:
            raise RuntimeError_(
                f"I don't know how to move '{stmt.direction}'.",
                stmt.location,
            )

    def _exec_make(self, stmt: MakeStatement, env: Environment) -> None:
        t = self.turtles.get(stmt.turtle_name)
        action = stmt.action
        if action == "hide":
            t.hide()
        elif action == "show":
            t.show()
        elif action == "pen_up":
            t.raise_pen()
        elif action == "pen_down":
            t.lower_pen()
        elif action == "erase_all":
            t.clear()
        elif action == "restart":
            t.reset()
        elif action == "home":
            t.home()
        elif action == "draw_circle":
            r = _to_number(self._eval(stmt.arg, env)) if stmt.arg else 0
            t.circle(r)
        elif action == "draw_dot":
            s = _to_number(self._eval(stmt.arg, env)) if stmt.arg else 0
            t.dot(s)
        elif action == "speed":
            s = _to_number(self._eval(stmt.arg, env)) if stmt.arg else 3
            t.set_speed(int(s))
        elif action == "go_to":
            # arg is a ListLiteral of [x, y]
            if not isinstance(stmt.arg, ListLiteral) or len(stmt.arg.elements) != 2:
                raise RuntimeError_(
                    f"'go to' needs two numbers, but I got something else.",
                    stmt.location,
                )
            x = _to_number(self._eval(stmt.arg.elements[0], env))
            y = _to_number(self._eval(stmt.arg.elements[1], env))
            t.goto_absolute(x, y)
        else:
            raise RuntimeError_(
                f"I don't know the turtle action '{action}'.",
                stmt.location,
            )

    def _exec_goto(self, stmt: GotoStatement, env: Environment) -> None:
        t = self.turtles.get(stmt.turtle_name)
        x_amount = _to_number(self._eval(stmt.x_amount, env))
        y_amount = _to_number(self._eval(stmt.y_amount, env))
        t.goto_relative(x_amount, stmt.x_dir, y_amount, stmt.y_dir)

    def _exec_set(self, stmt: SetStatement, env: Environment) -> None:
        name = stmt.turtle_name
        prop = stmt.property
        value = self._eval(stmt.value, env)

        # Check if this is a turtle (has a turtle with this name)
        try:
            t = self.turtles.get(name)
        except RuntimeError:
            t = None
        if t is not None:
            if prop == "pen color":
                t.set_pen_color(_to_text(value))
            elif prop == "pen size":
                t.set_pen_size(int(_to_number(value)))
            elif prop == "background":
                t.set_background(_to_text(value))
            else:
                raise RuntimeError_(
                    f"I don't know how to set '{prop}' on a turtle.",
                    stmt.location,
                )
            return

        # Check if this is a GUI widget or window
        try:
            self.gui.set_property(name, prop, value)
            return
        except ValueError:
            pass

        raise RuntimeError_(
            f"I don't know how to set '{prop}' on '{name}'.",
            stmt.location,
        )

    def _exec_widget_create(self, stmt: WidgetCreate, env: Environment) -> None:
        """`let btn be button "Click Me" on win`"""
        text = ""
        if stmt.args:
            text = _to_text(self._eval(stmt.args[0], env))
        parent_name = self._eval(stmt.parent, env)
        if isinstance(parent_name, str):
            pass  # already a string name
        else:
            parent_name = stmt.parent.name if hasattr(stmt.parent, 'name') else str(parent_name)
        try:
            self.gui.create_widget(stmt.widget_type, stmt.var_name, parent_name, text)
        except ValueError as e:
            raise RuntimeError_(str(e), stmt.location)

    def _exec_handle_event(self, stmt: HandleEvent, env: Environment) -> None:
        """`make win do on_click when btn clicked`"""
        window_name = self._eval(stmt.window, env)
        if not isinstance(window_name, str):
            window_name = stmt.window.name if hasattr(stmt.window, 'name') else str(window_name)
        widget_name = self._eval(stmt.widget, env)
        if not isinstance(widget_name, str):
            widget_name = stmt.widget.name if hasattr(stmt.widget, 'name') else str(widget_name)
        self.gui.handle_event(window_name, stmt.handler, widget_name, stmt.event)

    def _exec_place_widget(self, stmt: PlaceWidget, env: Environment) -> None:
        """`make win place btn at row 0 and column 0`"""
        window_name = self._eval(stmt.window, env)
        if not isinstance(window_name, str):
            window_name = stmt.window.name if hasattr(stmt.window, 'name') else str(window_name)
        widget_name = self._eval(stmt.widget, env)
        if not isinstance(widget_name, str):
            widget_name = stmt.widget.name if hasattr(stmt.widget, 'name') else str(widget_name)
        row = int(_to_number(self._eval(stmt.row, env)))
        col = int(_to_number(self._eval(stmt.column, env)))
        self.gui.place_widget(window_name, widget_name, row, col)

    def _exec_show_window(self, stmt: ShowWindow, env: Environment) -> None:
        """`show win`"""
        window_name = self._eval(stmt.window, env)
        if not isinstance(window_name, str):
            window_name = stmt.window.name if hasattr(stmt.window, 'name') else str(window_name)
        self.gui.show_window(window_name)

    def _exec_hide_window(self, stmt: HideWindow, env: Environment) -> None:
        """`hide win`"""
        window_name = self._eval(stmt.window, env)
        if not isinstance(window_name, str):
            window_name = stmt.window.name if hasattr(stmt.window, 'name') else str(window_name)
        self.gui.hide_window(window_name)

    _DISPATCH = {
        LetStatement: _exec_let,
        SayStatement: _exec_say,
        IfStatement: _exec_if,
        WhileStatement: _exec_while,
        RepeatStatement: _exec_repeat,
        ForEachStatement: _exec_for_each,
        FunctionDef: _exec_function_def,
        ReturnStatement: _exec_return,
        ExpressionStatement: _exec_expr_stmt,
        MoveStatement: _exec_move,
        MakeStatement: _exec_make,
        GotoStatement: _exec_goto,
        SetStatement: _exec_set,
        WidgetCreate: _exec_widget_create,
        HandleEvent: _exec_handle_event,
        PlaceWidget: _exec_place_widget,
        ShowWindow: _exec_show_window,
        HideWindow: _exec_hide_window,
    }

    # ---------- expressions ----------

    def _eval(self, expr, env: Environment) -> Any:
        if expr is None:
            return None
        method = self._EVAL_DISPATCH.get(type(expr))
        if method is None:
            raise RuntimeError_(
                f"I don't know how to evaluate a {type(expr).__name__}.",
                getattr(expr, "location", None),
            )
        return method(self, expr, env)

    def _eval_number(self, e: NumberLiteral, env):
        return e.value

    def _eval_string(self, e: StringLiteral, env):
        return e.value

    def _eval_bool(self, e: BoolLiteral, env):
        return e.value

    def _eval_nothing(self, e: NothingLiteral, env):
        return None

    def _eval_ident(self, e: Identifier, env):
        name = e.name
        try:
            return env.get(name)
        except KeyError:
            raise NameError_(
                f"I don't know what '{name}' means. "
                f"Did you forget to define it with `let {name} be ...`?",
                e.location,
            )

    def _eval_list(self, e: ListLiteral, env):
        return [self._eval(x, env) for x in e.elements]

    def _eval_concat(self, e: ConcatExpression, env):
        # `,` is the string-concat operator: convert each part to text and join.
        return "".join(_to_text(self._eval(p, env)) for p in e.parts)

    def _eval_binary(self, e: BinaryOp, env):
        op = e.op
        # Short-circuit logic
        if op == "and":
            left = self._eval(e.left, env)
            if not _to_bool(left):
                return left
            return self._eval(e.right, env)
        if op == "or":
            left = self._eval(e.left, env)
            if _to_bool(left):
                return left
            return self._eval(e.right, env)

        left = self._eval(e.left, env)
        right = self._eval(e.right, env)

        if op == "plus":
            ln, rn = _to_number(left), _to_number(right)
            return ln + rn
        if op == "minus":
            ln, rn = _to_number(left), _to_number(right)
            return ln - rn
        if op == "times":
            ln, rn = _to_number(left), _to_number(right)
            return ln * rn
        if op == "divided by":
            rn = _to_number(right)
            if rn == 0:
                raise RuntimeError_(
                    "I can't divide by zero. Math says no!",
                    e.right.location,
                )
            result = _to_number(left) / rn
            # If both operands were ints and the result is whole, return an int.
            if isinstance(left, int) and isinstance(right, int) and isinstance(result, float) and result.is_integer():
                return int(result)
            return result
        if op == "mod":
            ln, rn = _to_number(left), _to_number(right)
            if rn == 0:
                raise RuntimeError_(
                    "I can't mod by zero.",
                    e.right.location,
                )
            return ln % rn

        if op == "is":
            return left == right
        if op == "is not equal to":
            return left != right
        if op == "is greater than":
            ln, rn = _to_number(left), _to_number(right)
            return ln > rn
        if op == "is less than":
            ln, rn = _to_number(left), _to_number(right)
            return ln < rn
        if op == "is greater than or equal to":
            ln, rn = _to_number(left), _to_number(right)
            return ln >= rn
        if op == "is less than or equal to":
            ln, rn = _to_number(left), _to_number(right)
            return ln <= rn

        raise RuntimeError_(f"I don't know the operator '{op}'.", e.location)

    def _eval_unary(self, e: UnaryOp, env):
        if e.op == "not":
            return not _to_bool(self._eval(e.operand, env))
        if e.op == "minus":
            return -_to_number(self._eval(e.operand, env))
        raise RuntimeError_(f"I don't know the operator '{e.op}'.", e.location)

    def _eval_index(self, e: IndexExpression, env):
        coll = self._eval(e.collection, env)
        idx = self._eval(e.index, env)
        idx_n = int(_to_number(idx))
        if not isinstance(coll, list):
            raise TypeError_(
                f"I can't use 'at' on {_typename(coll)} ({_to_text(coll)}). "
                f"`at` only works on lists.",
                e.location,
            )
        if idx_n < 0:
            idx_n += len(coll)
        if idx_n < 0 or idx_n >= len(coll):
            raise RuntimeError_(
                f"I tried to get item {idx_n} from a list of size {len(coll)}, "
                f"but that item doesn't exist (lists start at 0 and go to {len(coll) - 1}).",
                e.index.location,
            )
        return coll[idx_n]

    def _eval_size(self, e: SizeExpression, env):
        coll = self._eval(e.collection, env)
        if isinstance(coll, list):
            return len(coll)
        if isinstance(coll, str):
            return len(coll)
        raise TypeError_(
            f"I can't get the size of {_typename(coll)} ({_to_text(coll)}). "
            f"Use `size of` on a list or some text.",
            e.location,
        )

    def _eval_with_added(self, e: WithAddedExpression, env):
        coll = self._eval(e.collection, env)
        if not isinstance(coll, list):
            raise TypeError_(
                f"I can only add to a list with 'with ... added', "
                f"but I got {_typename(coll)} ({_to_text(coll)}).",
                e.location,
            )
        value = self._eval(e.value, env)
        return coll + [value]

    def _eval_turtle_literal(self, e: TurtleLiteral, env):
        """`turtle` — a marker for "create a new turtle". We need a name to
        bind it to, but the parser already consumed the name via LetStatement.
        However, in the existing LetStatement executor, we just call
        `_eval(stmt.value, env)` and assign whatever it returns. So we
        return a sentinel that `_exec_let` recognizes.

        Actually, simpler: return a special wrapper and let the let-statement
        executor do the create-and-bind itself. But that requires changing
        the let executor. Cleaner: have `let ada be turtle` go through a
        special path.

        Decision: We return a `_TurtleFactory` sentinel here, and the
        let-statement executor checks for it and creates the turtle."""
        from src.turtle_runtime import Turtle as _T
        # Return a placeholder; _exec_let will detect TurtleLiteral and
        # create a new turtle with the bound name.
        return _turtle_factory_marker()

    def _eval_window_literal(self, e: WindowLiteral, env):
        """`window` — a marker sentinel; _exec_let detects it and creates the window."""
        return _window_factory_marker()

    def _eval_text_of(self, e: TextOf, env):
        """`text of btn` — read the current text value of a widget."""
        widget_name = self._eval(e.widget, env)
        if not isinstance(widget_name, str):
            widget_name = e.widget.name if hasattr(e.widget, 'name') else str(widget_name)
        return self.gui.get_text_of(widget_name)

    def _eval_call(self, e: CallExpression, env):
        name = e.callee
        # Turtle property access: `ada heading` / `ada x` / `ada y`.
        # The parser can't tell at parse time whether `ada` is a turtle
        # or a function, so we dispatch at runtime: if the first argument
        # is an Identifier and the callee is a Turtle, treat as property
        # read.
        if (len(e.arguments) == 1
                and isinstance(e.arguments[0], Identifier)
                and name in self.turtles.turtles):
            t = self.turtles.get(name)
            prop = e.arguments[0].name
            if prop == "heading":
                return t.heading
            if prop == "x":
                return t.x
            if prop == "y":
                return t.y
            raise RuntimeError_(
                f"I don't know what property '{prop}' means on a turtle. "
                f"Try 'heading', 'x', or 'y'.",
                e.location,
            )

        args = [self._eval(a, env) for a in e.arguments]

        # Built-in first
        if name in self._builtins:
            return self._builtins[name](args, e.location)

        # User-defined function
        func = env.get_function(name)
        if func is None:
            raise NameError_(
                f"I don't know a function called '{name}'.",
                e.location,
            )

        if len(func.params) != len(args):
            raise TypeError_(
                f"The function '{name}' expects {len(func.params)} argument"
                f"{'s' if len(func.params) != 1 else ''} "
                f"but I got {len(args)}.",
                e.location,
            )

        call_env = self.global_env.child() if func.name in self._builtins else env.child()
        for pname, pval in zip(func.params, args):
            call_env.define(pname, pval)
        try:
            self._exec_stmts(func.body, call_env)
        except _ReturnSignal as ret:
            return ret.value
        return None

    _EVAL_DISPATCH = {
        NumberLiteral: _eval_number,
        StringLiteral: _eval_string,
        BoolLiteral: _eval_bool,
        NothingLiteral: _eval_nothing,
        Identifier: _eval_ident,
        ListLiteral: _eval_list,
        ConcatExpression: _eval_concat,
        BinaryOp: _eval_binary,
        UnaryOp: _eval_unary,
        CallExpression: _eval_call,
        IndexExpression: _eval_index,
        SizeExpression: _eval_size,
        WithAddedExpression: _eval_with_added,
        TurtleLiteral: _eval_turtle_literal,
        WindowLiteral: _eval_window_literal,
        TextOf: _eval_text_of,
    }

