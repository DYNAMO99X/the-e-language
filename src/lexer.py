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
            else:
                raise LexerError(
                    f"I ran into a character I don't understand: '{c}' "
                    f"(line {self.line}, column {self.col}).",
                    self._loc(self.line, self.col),
                )

        self.tokens.append(Token(TokenType.EOF, "", self._loc(self.line, self.col)))
        return self.tokens
