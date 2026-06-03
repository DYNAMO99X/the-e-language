"""E Language Interpreter — Bundled for Pyodide (web playground).

This file combines all src/*.py modules into a single file so Pyodide
can load it without needing a file system.
"""
# --- src/errors.py ---
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class SourceLocation:
    line: int
    column: int
    name: str

class EError(Exception):
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

# --- src.tokens ---
from enum import Enum, auto
from dataclasses import dataclass as dc

class TokenType(Enum):
    NUMBER = auto()
    STRING = auto()
    IDENT = auto()
    LET = auto()
    BE = auto()
    SAY = auto()
    ASK = auto()
    IF = auto()
    THEN = auto()
    ELSE = auto()
    END = auto()
    WHILE = auto()
    REPEAT = auto()
    TIMES = auto()
    FOR = auto()
    EACH = auto()
    IN = auto()
    TO = auto()
    RETURN = auto()
    TRUE = auto()
    FALSE = auto()
    NOTHING = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    IS = auto()
    IS_NOT_EQUAL = auto()
    IS_GREATER = auto()
    IS_LESS = auto()
    IS_GREATER_EQ = auto()
    IS_LESS_EQ = auto()
    PLUS = auto()
    MINUS = auto()
    TIMES_KW = auto()
    DIVIDED = auto()
    BY = auto()
    MOD = auto()
    COMMA = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    AT = auto()
    WITH = auto()
    ADDED = auto()
    SIZE = auto()
    OF = auto()
    TURTLE = auto()
    MOVE = auto()
    MAKE = auto()
    GOTO = auto()
    SET = auto()
    NEWLINE = auto()
    EOF = auto()

@dc
class Token:
    type: TokenType
    value: object
    location: SourceLocation

# --- src.ast_nodes ---
from dataclasses import dataclass, field
from typing import List, Any, Optional

@dc
class Program:
    statements: List[Any] = field(default_factory=list)
    location: Optional[SourceLocation] = None

class Statement: pass

@dc
class LetStatement(Statement):
    name: str = ""
    value: Any = None
    location: Optional[SourceLocation] = None

@dc
class SayStatement(Statement):
    parts: List[Any] = field(default_factory=list)
    location: Optional[SourceLocation] = None

@dc
class AskStatement(Statement):
    prompt: Any = None
    location: Optional[SourceLocation] = None

@dc
class IfStatement(Statement):
    condition: Any = None
    then_branch: List[Statement] = field(default_factory=list)
    else_branch: Optional[List[Statement]] = None
    location: Optional[SourceLocation] = None

@dc
class WhileStatement(Statement):
    condition: Any = None
    body: List[Statement] = field(default_factory=list)
    location: Optional[SourceLocation] = None

@dc
class RepeatStatement(Statement):
    count: Any = None
    body: List[Statement] = field(default_factory=list)
    location: Optional[SourceLocation] = None

@dc
class ForEachStatement(Statement):
    var_name: str = ""
    iterable: Any = None
    body: List[Statement] = field(default_factory=list)
    location: Optional[SourceLocation] = None

@dc
class FunctionDef(Statement):
    name: str = ""
    params: List[str] = field(default_factory=list)
    body: List[Statement] = field(default_factory=list)
    location: Optional[SourceLocation] = None

@dc
class ReturnStatement(Statement):
    value: Any = None
    location: Optional[SourceLocation] = None

@dc
class ExpressionStatement(Statement):
    expression: Any = None
    location: Optional[SourceLocation] = None

class Expression: pass

@dc
class NumberLiteral(Expression):
    value: float = 0
    location: Optional[SourceLocation] = None

@dc
class StringLiteral(Expression):
    value: str = ""
    location: Optional[SourceLocation] = None

@dc
class BoolLiteral(Expression):
    value: bool = False
    location: Optional[SourceLocation] = None

@dc
class NothingLiteral(Expression):
    location: Optional[SourceLocation] = None

@dc
class Identifier(Expression):
    name: str = ""
    location: Optional[SourceLocation] = None

@dc
class ListLiteral(Expression):
    elements: List[Expression] = field(default_factory=list)
    location: Optional[SourceLocation] = None

@dc
class ConcatExpression(Expression):
    parts: List[Expression] = field(default_factory=list)
    location: Optional[SourceLocation] = None

@dc
class BinaryOp(Expression):
    op: str = ""
    left: Expression = None
    right: Expression = None
    location: Optional[SourceLocation] = None

@dc
class UnaryOp(Expression):
    op: str = ""
    operand: Expression = None
    location: Optional[SourceLocation] = None

@dc
class CallExpression(Expression):
    callee: str = ""
    arguments: List[Expression] = field(default_factory=list)
    location: Optional[SourceLocation] = None

@dc
class IndexExpression(Expression):
    collection: Expression = None
    index: Expression = None
    location: Optional[SourceLocation] = None

@dc
class SizeExpression(Expression):
    collection: Expression = None
    location: Optional[SourceLocation] = None

@dc
class WithAddedExpression(Expression):
    collection: Expression = None
    value: Expression = None
    location: Optional[SourceLocation] = None

@dc
class TurtleLiteral(Expression):
    location: Optional[SourceLocation] = None

@dc
class MoveStatement(Statement):
    turtle_name: str = ""
    direction: str = ""
    amount: Any = None
    location: Optional[SourceLocation] = None

@dc
class MakeStatement(Statement):
    turtle_name: str = ""
    action: str = ""
    arg: Optional[Expression] = None
    location: Optional[SourceLocation] = None

@dc
class GotoStatement(Statement):
    turtle_name: str = ""
    x_amount: Any = None
    x_dir: str = ""
    y_amount: Any = None
    y_dir: str = ""
    location: Optional[SourceLocation] = None

@dc
class SetStatement(Statement):
    turtle_name: str = ""
    property: str = ""
    value: Any = None
    location: Optional[SourceLocation] = None

@dc
class TurtlePropertyAccess(Expression):
    turtle_name: str = ""
    property: str = ""
    location: Optional[SourceLocation] = None

# --- src.environment ---
class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.variables = {}
        self.functions = {}

    def define(self, name, value):
        self.variables[name] = value

    def get(self, name):
        env = self
        while env is not None:
            if name in env.variables:
                return env.variables[name]
            env = env.parent
        raise KeyError(name)

    def set(self, name, value):
        env = self
        while env is not None:
            if name in env.variables:
                env.variables[name] = value
                return
            env = env.parent
        raise KeyError(name)

    def has(self, name):
        env = self
        while env is not None:
            if name in env.variables:
                return True
            env = env.parent
        return False

    def define_function(self, name, func):
        self.functions[name] = func

    def get_function(self, name):
        env = self
        while env is not None:
            if name in env.functions:
                return env.functions[name]
            env = env.parent
        return None

    def child(self):
        return Environment(parent=self)

# --- src.lexer ---
from typing import List as _List

_MULTI_WORD = {
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

_KEYWORDS = {
    "let": TokenType.LET, "be": TokenType.BE, "say": TokenType.SAY,
    "ask": TokenType.ASK, "if": TokenType.IF, "then": TokenType.THEN,
    "else": TokenType.ELSE, "end": TokenType.END, "while": TokenType.WHILE,
    "repeat": TokenType.REPEAT, "times": TokenType.TIMES,
    "for": TokenType.FOR, "each": TokenType.EACH, "in": TokenType.IN,
    "to": TokenType.TO, "return": TokenType.RETURN,
    "true": TokenType.TRUE, "false": TokenType.FALSE,
    "nothing": TokenType.NOTHING,
    "and": TokenType.AND, "or": TokenType.OR, "not": TokenType.NOT,
    "plus": TokenType.PLUS, "minus": TokenType.MINUS, "mod": TokenType.MOD,
    "is": TokenType.IS, "by": TokenType.BY, "at": TokenType.AT,
    "with": TokenType.WITH, "added": TokenType.ADDED,
    "size": TokenType.SIZE, "of": TokenType.OF,
    "turtle": TokenType.TURTLE, "move": TokenType.MOVE,
    "make": TokenType.MAKE, "goto": TokenType.GOTO, "set": TokenType.SET,
}

class Lexer:
    def __init__(self, source, name="<source>"):
        self.source = source
        self.name = name
        self.start = 0
        self.current = 0
        self.line = 1
        self.col = 1
        self.tokens = []

    def _loc(self, line, col):
        return SourceLocation(line=line, column=col, name=self.name)

    def _is_at_end(self):
        return self.current >= len(self.source)

    def _peek(self, offset=0):
        idx = self.current + offset
        if idx >= len(self.source):
            return "\0"
        return self.source[idx]

    def _advance(self):
        ch = self.source[self.current]
        self.current += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _add(self, ttype, value=None, loc=None):
        if value is None:
            value = self.source[self.start:self.current]
        if loc is None:
            loc = self._loc(self.line, self.col)
        self.tokens.append(Token(ttype, value, loc))

    def _word_at(self, pos):
        i = pos
        while i < len(self.source) and (self.source[i].isalnum() or self.source[i] == "_"):
            i += 1
        return self.source[pos:i], i

    def _try_multi_word(self, word_text, word_lower):
        if word_lower not in _MULTI_WORD:
            return False
        for tail, ttype in _MULTI_WORD[word_lower]:
            probe = self.current
            if probe >= len(self.source) or self.source[probe] not in (" ", "\t"):
                continue
            probe += 1
            matched = []
            ok = True
            for i, expected in enumerate(tail):
                w, end = self._word_at(probe)
                if w.lower() != expected:
                    ok = False
                    break
                matched.append(w)
                probe = end
                is_last = (i == len(tail) - 1)
                if not is_last:
                    if probe >= len(self.source) or self.source[probe] not in (" ", "\t"):
                        ok = False
                        break
                    probe += 1
            if not ok:
                continue
            if probe < len(self.source):
                ch = self.source[probe]
                if ch.isalnum() or ch == "_":
                    continue
            while self.current < probe:
                self._advance()
            self._add(ttype, word_text + " " + " ".join(matched))
            return True
        return False

    def _string(self, quote_char):
        start_line = self.line
        start_col = self.col
        self._advance()
        value_chars = []
        while not self._is_at_end() and self._peek() != quote_char:
            ch = self._advance()
            if ch == "\\" and not self._is_at_end():
                esc = self._advance()
                mapping = {"n": "\n", "t": "\t", "\\": "\\", '"': '"', "'": "'", "`": "`"}
                value_chars.append(mapping.get(esc, esc))
            else:
                value_chars.append(ch)
        if self._is_at_end():
            raise LexerError(
                f"I started reading a string on line {start_line} but never found the closing {quote_char}.",
                self._loc(start_line, start_col),
            )
        self._advance()
        self._add(TokenType.STRING, "".join(value_chars), loc=self._loc(start_line, start_col))

    def _number(self, is_negative=False):
        if is_negative:
            self._advance()
        while not self._is_at_end() and self._peek().isdigit():
            self._advance()
        if self._peek() == "." and self._peek(1).isdigit():
            self._advance()
            while not self._is_at_end() and self._peek().isdigit():
                self._advance()
        text = self.source[self.start:self.current]
        try:
            value = float(text)
            if value.is_integer() and "." not in text:
                value = int(value)
        except ValueError:
            raise LexerError(
                f"I tried to read a number on line {self.line} but '{text}' is not a valid number.",
                self._loc(self.line, self.col),
            )
        self._add(TokenType.NUMBER, value)

    def _word(self):
        while not self._is_at_end() and (self._peek().isalnum() or self._peek() == "_"):
            self._advance()
        word_text = self.source[self.start:self.current]
        word_lower = word_text.lower()
        if self._try_multi_word(word_text, word_lower):
            return
        if word_lower in _KEYWORDS:
            self._add(_KEYWORDS[word_lower], word_text)
            return
        self._add(TokenType.IDENT, word_text)

    def _is_value_position(self):
        if not self.tokens:
            return False
        prev_type = self.tokens[-1].type
        value_enders = {
            TokenType.NUMBER, TokenType.STRING, TokenType.IDENT,
            TokenType.TRUE, TokenType.FALSE, TokenType.NOTHING,
            TokenType.RPAREN, TokenType.RBRACKET,
        }
        return prev_type in value_enders

    def tokenize(self):
        while not self._is_at_end():
            self.start = self.current
            c = self._peek()
            if c in (" ", "\t", "\r"):
                self._advance()
            elif c == "\n":
                self._add(TokenType.NEWLINE, "\n")
                self._advance()
            elif c == "-" and self._peek(1) == "-":
                while not self._is_at_end() and self._peek() != "\n":
                    self._advance()
            elif c in ('"', "'", "`"):
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
                        f"I ran into a character I don't understand: '!' (line {self.line}, column {self.col}).",
                        self._loc(self.line, self.col),
                    )
            elif c == "-" and self._peek(1).isdigit() and not self._is_value_position():
                self._number(is_negative=True)
            elif c == "-":
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
                    f"I ran into a character I don't understand: '{c}' (line {self.line}, column {self.col}).",
                    self._loc(self.line, self.col),
                )
        self.tokens.append(Token(TokenType.EOF, "", self._loc(self.line, self.col)))
        return self.tokens

# --- src.parser ---
from typing import Set as _Set

_EXPR_START = {
    TokenType.NUMBER, TokenType.STRING, TokenType.IDENT,
    TokenType.TRUE, TokenType.FALSE, TokenType.NOTHING,
    TokenType.LPAREN, TokenType.LBRACKET, TokenType.NOT, TokenType.SIZE,
}
_BLOCK_END = {TokenType.END, TokenType.ELSE, TokenType.EOF}
_STMT_START = {
    TokenType.LET, TokenType.SAY, TokenType.IF, TokenType.WHILE,
    TokenType.REPEAT, TokenType.FOR, TokenType.TO, TokenType.RETURN,
    TokenType.MOVE, TokenType.MAKE, TokenType.SET,
}

class Parser:
    def __init__(self, tokens, name="<source>"):
        self.tokens = tokens
        self.name = name
        self.pos = 0

    def _peek(self, offset=0):
        idx = self.pos + offset
        if idx >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[idx]

    def _at_end(self):
        return self._peek().type == TokenType.EOF

    def _advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def _check(self, ttype):
        return self._peek().type == ttype

    def _match(self, *ttype):
        if self._peek().type in ttype:
            return self._advance()
        return None

    def _expect(self, ttype, message):
        tok = self._peek()
        if tok.type != ttype:
            raise ParseError(
                f"{message} (I found '{tok.value}' on line {tok.location.line}, column {tok.location.column} instead.)",
                tok.location,
            )
        return self._advance()

    def _skip_newlines(self):
        while self._check(TokenType.NEWLINE):
            self._advance()

    def _error(self, message):
        tok = self._peek()
        return ParseError(
            f"{message} (line {tok.location.line}, column {tok.location.column}, near '{tok.value}')",
            tok.location,
        )

    def parse(self):
        statements = []
        self._skip_newlines()
        while not self._at_end():
            stmt = self._parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self._skip_newlines()
        return Program(statements=statements, location=SourceLocation(1, 1, self.name))

    def _parse_statement(self):
        tok = self._peek()
        if tok.type == TokenType.LET: return self._parse_let()
        if tok.type == TokenType.SAY: return self._parse_say()
        if tok.type == TokenType.IF: return self._parse_if()
        if tok.type == TokenType.WHILE: return self._parse_while()
        if tok.type == TokenType.REPEAT: return self._parse_repeat()
        if tok.type == TokenType.FOR: return self._parse_for()
        if tok.type == TokenType.TO: return self._parse_function_def()
        if tok.type == TokenType.RETURN: return self._parse_return()
        if tok.type == TokenType.MOVE: return self._parse_move()
        if tok.type == TokenType.MAKE: return self._parse_make()
        if tok.type == TokenType.SET: return self._parse_set()
        expr = self._parse_expression()
        if expr is None: return None
        return ExpressionStatement(expression=expr, location=expr.location)

    def _parse_let(self):
        let_tok = self._advance()
        name_tok = self._expect(TokenType.IDENT, "After 'let' I expected a name for the variable")
        self._expect(TokenType.BE, "After the variable name I expected 'be'")
        value = self._parse_expression()
        if value is None: raise self._error("After 'be' I expected a value for the variable")
        return LetStatement(name=name_tok.value, value=value, location=let_tok.location)

    def _parse_say(self):
        say_tok = self._advance()
        expr = self._parse_expression()
        if expr is None: raise self._error("After 'say' I expected something to say")
        return SayStatement(parts=[expr], location=say_tok.location)

    def _parse_if(self):
        if_tok = self._advance()
        condition = self._parse_expression()
        if condition is None: raise self._error("After 'if' I expected a condition")
        self._skip_newlines()
        if self._check(TokenType.THEN):
            self._advance()
            self._skip_newlines()
        then_branch = self._parse_block(_BLOCK_END)
        else_branch = None
        consumed_end = False
        if self._check(TokenType.ELSE):
            self._advance()
            if self._check(TokenType.IF):
                else_branch = [self._parse_if()]
                consumed_end = True
            else:
                self._skip_newlines()
                else_branch = self._parse_block(_BLOCK_END)
        if not consumed_end:
            self._expect(TokenType.END, "I was looking for 'end' to finish the if")
        return IfStatement(condition=condition, then_branch=then_branch, else_branch=else_branch, location=if_tok.location)

    def _parse_while(self):
        w_tok = self._advance()
        condition = self._parse_expression()
        if condition is None: raise self._error("After 'while' I expected a condition")
        self._skip_newlines()
        body = self._parse_block(_BLOCK_END)
        self._expect(TokenType.END, "I was looking for 'end' to finish the while loop")
        return WhileStatement(condition=condition, body=body, location=w_tok.location)

    def _parse_repeat(self):
        r_tok = self._advance()
        count = self._parse_primary()
        if count is None: raise self._error("After 'repeat' I expected a number")
        self._skip_newlines()
        self._expect(TokenType.TIMES, "After the number I expected 'times'")
        self._skip_newlines()
        body = self._parse_block(_BLOCK_END)
        self._expect(TokenType.END, "I was looking for 'end' to finish the repeat loop")
        return RepeatStatement(count=count, body=body, location=r_tok.location)

    def _parse_for(self):
        f_tok = self._advance()
        self._expect(TokenType.EACH, "After 'for' I expected 'each'")
        var_tok = self._expect(TokenType.IDENT, "After 'for each' I expected a variable name")
        self._expect(TokenType.IN, "After the variable name I expected 'in'")
        iterable = self._parse_or()
        if iterable is None: raise self._error("After 'in' I expected something to loop over")
        self._skip_newlines()
        body = self._parse_block(_BLOCK_END)
        self._expect(TokenType.END, "I was looking for 'end' to finish the for loop")
        return ForEachStatement(var_name=var_tok.value, iterable=iterable, body=body, location=f_tok.location)

    def _parse_function_def(self):
        to_tok = self._advance()
        name_tok = self._expect(TokenType.IDENT, "After 'to' I expected a function name")
        params = []
        while self._peek().type == TokenType.IDENT:
            params.append(self._advance().value)
        if not params:
            raise self._error(f"The function '{name_tok.value}' has no parameters. Functions need at least one name between 'to' and the body.")
        self._skip_newlines()
        body = self._parse_block(_BLOCK_END)
        self._expect(TokenType.END, "I was looking for 'end' to finish the function")
        return FunctionDef(name=name_tok.value, params=params, body=body, location=to_tok.location)

    def _parse_return(self):
        r_tok = self._advance()
        if (self._peek().type in _BLOCK_END or self._peek().type == TokenType.NEWLINE or self._peek().type in _STMT_START):
            return ReturnStatement(value=None, location=r_tok.location)
        value = self._parse_expression()
        return ReturnStatement(value=value, location=r_tok.location)

    def _parse_block(self, end_tokens):
        stmts = []
        while not self._at_end() and self._peek().type not in end_tokens:
            stmt = self._parse_statement()
            if stmt is not None: stmts.append(stmt)
            self._skip_newlines()
        return stmts

    def _parse_expression(self):
        left = self._parse_or()
        if left is None: return None
        if self._check(TokenType.COMMA):
            parts = [left]
            while self._check(TokenType.COMMA):
                self._advance()
                nxt = self._parse_or()
                if nxt is None: raise self._error("After ',' I expected another value")
                parts.append(nxt)
            return ConcatExpression(parts=parts, location=left.location)
        return left

    def _parse_or(self):
        left = self._parse_and()
        while left is not None and self._check(TokenType.OR):
            self._advance()
            right = self._parse_and()
            if right is None: raise self._error("After 'or' I expected a value")
            left = BinaryOp(op="or", left=left, right=right, location=left.location)
        return left

    def _parse_and(self):
        left = self._parse_unary_logic()
        while left is not None and self._check(TokenType.AND):
            self._advance()
            right = self._parse_unary_logic()
            if right is None: raise self._error("After 'and' I expected a value")
            left = BinaryOp(op="and", left=left, right=right, location=left.location)
        return left

    def _parse_unary_logic(self):
        if self._check(TokenType.NOT):
            op_tok = self._advance()
            operand = self._parse_unary_logic()
            if operand is None: raise self._error("After 'not' I expected a value")
            return UnaryOp(op="not", operand=operand, location=op_tok.location)
        return self._parse_comparison()

    def _parse_comparison(self):
        left = self._parse_additive()
        if left is None: return None
        comp_map = {
            TokenType.IS: "is", TokenType.IS_NOT_EQUAL: "is not equal to",
            TokenType.IS_GREATER: "is greater than", TokenType.IS_LESS: "is less than",
            TokenType.IS_GREATER_EQ: "is greater than or equal to",
            TokenType.IS_LESS_EQ: "is less than or equal to",
        }
        if self._peek().type in comp_map:
            op_tok = self._advance()
            right = self._parse_additive()
            if right is None: raise self._error(f"After '{op_tok.value}' I expected a value to compare with")
            return BinaryOp(op=comp_map[op_tok.type], left=left, right=right, location=op_tok.location)
        return left

    def _parse_additive(self):
        left = self._parse_multiplicative()
        while left is not None and self._peek().type in (TokenType.PLUS, TokenType.MINUS):
            op_tok = self._advance()
            right = self._parse_multiplicative()
            if right is None: raise self._error(f"After '{op_tok.value}' I expected a value")
            op = "plus" if op_tok.type == TokenType.PLUS else "minus"
            left = BinaryOp(op=op, left=left, right=right, location=left.location)
        return left

    def _parse_multiplicative(self):
        left = self._parse_unary()
        while left is not None and self._peek().type in (TokenType.TIMES, TokenType.DIVIDED, TokenType.MOD):
            op_tok = self._advance()
            right = self._parse_unary()
            if right is None: raise self._error(f"After '{op_tok.value}' I expected a value")
            if op_tok.type == TokenType.TIMES: op = "times"
            elif op_tok.type == TokenType.DIVIDED: op = "divided by"
            else: op = "mod"
            left = BinaryOp(op=op, left=left, right=right, location=left.location)
        return left

    def _parse_unary(self):
        if self._check(TokenType.MINUS):
            op_tok = self._advance()
            operand = self._parse_unary()
            if operand is None: raise self._error("After '-' I expected a value")
            return UnaryOp(op="minus", operand=operand, location=op_tok.location)
        return self._parse_postfix()

    def _parse_postfix(self):
        expr = self._parse_size_of_or_primary()
        while expr is not None and self._check(TokenType.AT):
            self._advance()
            index = self._parse_unary()
            if index is None: raise self._error("After 'at' I expected an index value")
            expr = IndexExpression(collection=expr, index=index, location=expr.location)
        if expr is not None and self._check(TokenType.WITH):
            self._advance()
            value = self._parse_unary()
            if value is None: raise self._error("After 'with' I expected a value to add")
            self._expect(TokenType.ADDED, "After the value I expected 'added'")
            expr = WithAddedExpression(collection=expr, value=value, location=expr.location)
        return expr

    def _parse_size_of_or_primary(self):
        if self._check(TokenType.SIZE):
            op_tok = self._advance()
            self._expect(TokenType.OF, "After 'size' I expected 'of'")
            operand = self._parse_size_of_or_primary()
            if operand is None: raise self._error("After 'size of' I expected a value")
            return SizeExpression(collection=operand, location=op_tok.location)
        return self._parse_primary()

    def _parse_primary(self):
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
            if expr is None: raise self._error("Inside '(' I expected a value")
            self._expect(TokenType.RPAREN, "I was looking for ')'")
            return expr
        if tok.type == TokenType.LBRACKET:
            return self._parse_list_literal()
        if tok.type == TokenType.IDENT:
            return self._parse_ident_or_call()
        if tok.type == TokenType.ASK:
            return self._parse_ask()
        return None

    def _parse_ask(self):
        ask_tok = self._advance()
        prompt = self._parse_expression()
        if prompt is None: raise self._error("After 'ask' I expected a prompt string")
        return CallExpression(callee="ask", arguments=[prompt], location=ask_tok.location)

    def _parse_ident_or_call(self):
        name_tok = self._advance()
        if self._peek().type in _EXPR_START:
            args = [self._parse_call_arg()]
            while self._check(TokenType.COMMA):
                self._advance()
                nxt = self._parse_call_arg()
                if nxt is None: raise self._error("After ',' in a function call I expected a value")
                args.append(nxt)
            return CallExpression(callee=name_tok.value, arguments=args, location=name_tok.location)
        return Identifier(name=name_tok.value, location=name_tok.location)

    def _parse_call_arg(self):
        expr = self._parse_primary()
        if expr is None: return None
        while self._check(TokenType.AT):
            self._advance()
            index = self._parse_call_arg()
            if index is None: raise self._error("After 'at' I expected an index value")
            expr = IndexExpression(collection=expr, index=index, location=expr.location)
        if self._check(TokenType.WITH):
            self._advance()
            value = self._parse_call_arg()
            if value is None: raise self._error("After 'with' I expected a value to add")
            self._expect(TokenType.ADDED, "After the value I expected 'added'")
            expr = WithAddedExpression(collection=expr, value=value, location=expr.location)
        return expr

    def _parse_list_literal(self):
        lb_tok = self._advance()
        elements = []
        self._skip_newlines()
        if not self._check(TokenType.RBRACKET):
            first = self._parse_or()
            if first is None: raise self._error("Inside '[' I expected a value")
            elements.append(first)
            while self._check(TokenType.COMMA):
                self._advance()
                self._skip_newlines()
                if self._check(TokenType.RBRACKET): break
                nxt = self._parse_or()
                if nxt is None: raise self._error("Inside '[' I expected a value after ','")
                elements.append(nxt)
        self._skip_newlines()
        self._expect(TokenType.RBRACKET, "I was looking for ']' to close the list")
        return ListLiteral(elements=elements, location=lb_tok.location)

    def _expect_ident(self, message):
        tok = self._peek()
        if tok.type != TokenType.IDENT:
            raise self._error(message)
        self._advance()
        return str(tok.value)

    def _parse_move(self):
        move_tok = self._advance()
        name = self._expect_ident("After 'move' I expected a turtle's name")
        dir_tok = self._peek()
        direction = None
        if dir_tok.type == TokenType.IDENT:
            word = str(dir_tok.value).lower()
            if word in ("forward", "backward", "left", "right"):
                direction = word
                self._advance()
        if direction is None:
            raise self._error("After 'move <turtle>' I expected 'forward', 'backward', 'left', or 'right'")
        amount = self._parse_expression()
        if amount is None: raise self._error(f"After 'move <turtle> {direction}' I expected a number")
        return MoveStatement(turtle_name=name, direction=direction, amount=amount, location=move_tok.location)

    def _parse_make(self):
        make_tok = self._advance()
        name = self._expect_ident("After 'make' I expected a turtle's name")
        if self._check(TokenType.GOTO):
            return self._parse_make_goto_relative(make_tok, name)
        nxt = self._peek()
        if nxt.type != TokenType.IDENT:
            raise self._error(f"After 'make {name}' I expected an action")
        word = str(nxt.value).lower()
        self._advance()
        if word == "go" and self._check(TokenType.IDENT) and str(self._peek().value).lower() == "home":
            self._advance()
            return MakeStatement(turtle_name=name, action="home", arg=None, location=make_tok.location)
        if word == "go" and self._check(TokenType.TO):
            self._advance()
            x = self._parse_additive()
            if x is None: raise self._error("After 'make X go to' I expected a number for x")
            self._expect(TokenType.AND, "After the x value I expected 'and'")
            y = self._parse_additive()
            if y is None: raise self._error("After 'and' I expected a number for y")
            return MakeStatement(turtle_name=name, action="go_to", arg=ListLiteral(elements=[x, y], location=x.location), location=make_tok.location)
        if word == "close" and self._check(TokenType.IDENT) and str(self._peek().value).lower() == "pen":
            self._advance()
            return MakeStatement(turtle_name=name, action="pen_up", arg=None, location=make_tok.location)
        if word == "open" and self._check(TokenType.IDENT) and str(self._peek().value).lower() == "pen":
            self._advance()
            return MakeStatement(turtle_name=name, action="pen_down", arg=None, location=make_tok.location)
        if word == "erase" and self._check(TokenType.IDENT) and str(self._peek().value).lower() == "all":
            self._advance()
            return MakeStatement(turtle_name=name, action="erase_all", arg=None, location=make_tok.location)
        if word == "draw":
            shape_tok = self._peek()
            if shape_tok.type != TokenType.IDENT:
                raise self._error("After 'make X draw' I expected 'circle' or 'dot'")
            shape = str(shape_tok.value).lower()
            if shape not in ("circle", "dot"):
                raise self._error(f"I don't know how to draw a '{shape}'. Try 'circle' or 'dot'.")
            self._advance()
            arg = self._parse_expression()
            if arg is None: raise self._error(f"After 'make X draw {shape}' I expected a number for the size")
            return MakeStatement(turtle_name=name, action=f"draw_{shape}", arg=arg, location=make_tok.location)
        if word in ("hide", "show", "restart"):
            return MakeStatement(turtle_name=name, action=word, arg=None, location=make_tok.location)
        if word == "speed":
            arg = self._parse_expression()
            if arg is None: raise self._error("After 'make X speed' I expected a number from 0 to 10")
            return MakeStatement(turtle_name=name, action="speed", arg=arg, location=make_tok.location)
        raise self._error(f"I don't know the action '{word}' for a turtle.")

    def _parse_make_goto_relative(self, make_tok, name):
        self._advance()
        x_amount = self._parse_additive()
        if x_amount is None: raise self._error("After 'goto' I expected a number for the x amount")
        x_dir_tok = self._peek()
        if x_dir_tok.type != TokenType.IDENT or str(x_dir_tok.value).lower() not in ("right", "left"):
            raise self._error("After the x amount I expected 'right' or 'left'")
        x_dir = str(x_dir_tok.value).lower()
        self._advance()
        self._expect(TokenType.AND, "After the x direction I expected 'and'")
        y_amount = self._parse_additive()
        if y_amount is None: raise self._error("After 'and' I expected a number for the y amount")
        y_dir_tok = self._peek()
        if y_dir_tok.type != TokenType.IDENT or str(y_dir_tok.value).lower() not in ("up", "down"):
            raise self._error("After the y amount I expected 'up' or 'down'")
        y_dir = str(y_dir_tok.value).lower()
        self._advance()
        return GotoStatement(turtle_name=name, x_amount=x_amount, x_dir=x_dir, y_amount=y_amount, y_dir=y_dir, location=make_tok.location)

    def _parse_set(self):
        set_tok = self._advance()
        name = self._expect_ident("After 'set' I expected a turtle's name")
        property_name = self._parse_set_property(name)
        self._expect(TokenType.TO, "After the property name I expected 'to'")
        value = self._parse_expression()
        if value is None: raise self._error(f"After 'set {name} {property_name} to' I expected a value")
        return SetStatement(turtle_name=name, property=property_name, value=value, location=set_tok.location)

    def _parse_set_property(self, turtle_name):
        first = self._peek()
        if first.type != TokenType.IDENT:
            raise self._error(f"After 'set {turtle_name}' I expected a property name")
        word = str(first.value).lower()
        if word == "pen":
            self._advance()
            second = self._peek()
            second_text = str(second.value).lower() if second.value is not None else ""
            if second_text not in ("color", "size"):
                raise self._error(f"After 'set {turtle_name} pen' I expected 'color' or 'size'")
            self._advance()
            return f"pen {second_text}"
        self._advance()
        return word

# --- src.interpreter ---
import math
import random as _random

def _typename(v):
    if isinstance(v, bool): return "true/false"
    if isinstance(v, (int, float)): return "number"
    if isinstance(v, str): return "text"
    if isinstance(v, list): return "list"
    if v is None: return "nothing"
    return type(v).__name__

def _to_text(v):
    if v is None: return "nothing"
    if isinstance(v, bool): return "true" if v else "false"
    if isinstance(v, list): return "[" + ", ".join(_to_text(x) for x in v) + "]"
    return str(v)

def _to_number(v):
    if isinstance(v, bool):
        raise TypeError_(f"I can't do math with {_typename(v)} ({_to_text(v)}). Use a number.")
    if isinstance(v, (int, float)): return v
    if isinstance(v, str):
        try:
            n = float(v)
            if n.is_integer(): return int(n)
            return n
        except ValueError:
            raise TypeError_(f"I can't turn the text \"{v}\" into a number.")
    raise TypeError_(f"I can't do math with {_typename(v)} ({_to_text(v)}). Use a number.")

def _to_bool(v):
    if v is None or v is False: return False
    return True

class _ReturnSignal(Exception):
    def __init__(self, value): self.value = value

class _turtle_factory_marker:
    _instance = None
    def __new__(cls):
        if cls._instance is None: cls._instance = super().__new__(cls)
        return cls._instance
    def __repr__(self): return "<turtle-factory>"

# --- src.turtle_runtime (text mode only for web) ---
class Turtle:
    def __init__(self, name, mode="text"):
        self.name = name
        self.mode = "text"
        self.log = []
        self.x = 0.0
        self.y = 0.0
        self.heading = 0.0
        self.pen_down = True
        self.pen_color = "black"
        self.pen_size = 1
        self.background = "white"
        self.visible = True
        self.speed = 3

    def _log(self, msg):
        self.log.append(f">> {msg}")

    def forward(self, n):
        rad = math.radians(self.heading)
        self.x += n * math.cos(rad)
        self.y += n * math.sin(rad)
        self._log(f"forward {n}")

    def backward(self, n):
        rad = math.radians(self.heading)
        self.x -= n * math.cos(rad)
        self.y -= n * math.sin(rad)
        self._log(f"backward {n}")

    def left(self, n):
        self.heading = (self.heading + n) % 360
        self._log(f"left {n}")

    def right(self, n):
        self.heading = (self.heading - n) % 360
        self._log(f"right {n}")

    def hide(self):
        self.visible = False
        self._log("hide")

    def show(self):
        self.visible = True
        self._log("show")

    def raise_pen(self):
        self.pen_down = False
        self._log("pen_up")

    def lower_pen(self):
        self.pen_down = True
        self._log("pen_down")

    def clear(self):
        self.log.clear()
        self._log("erase_all")

    def home(self):
        self.x = 0.0; self.y = 0.0; self.heading = 0.0
        self._log("home")

    def reset(self):
        self.x = 0.0; self.y = 0.0; self.heading = 0.0
        self.pen_down = True; self.pen_color = "black"; self.pen_size = 1
        self.background = "white"; self.visible = True; self.speed = 3
        self.log.clear()
        self._log("restart")

    def circle(self, r):
        self._log(f"draw_circle {r}")

    def dot(self, size):
        self._log(f"draw_dot {size}")

    def goto_relative(self, x_amount, x_dir, y_amount, y_dir):
        dx = x_amount if x_dir == "right" else -x_amount
        dy = y_amount if y_dir == "up" else -y_amount
        self.x += dx; self.y += dy
        self._log(f"goto {x_amount} {x_dir} and {y_amount} {y_dir}")

    def goto_absolute(self, x, y):
        self.x = x; self.y = y
        self._log(f"go_to {x} and {y}")

    def set_speed(self, n):
        self.speed = max(0, min(10, int(n)))
        self._log(f"speed {self.speed}")

    def set_pen_color(self, color):
        self.pen_color = str(color)
        self._log(f"pen_color {self.pen_color}")

    def set_pen_size(self, n):
        self.pen_size = max(1, int(n))
        self._log(f"pen_size {self.pen_size}")

    def set_background(self, color):
        self.background = str(color)
        self._log(f"background {self.background}")

class TurtleManager:
    def __init__(self, requested_mode="text"):
        self.turtles = {}

    def create(self, name):
        t = Turtle(name, "text")
        self.turtles[name] = t
        return t

    def get(self, name):
        if name not in self.turtles:
            raise RuntimeError(f"I don't know a turtle called '{name}'.")
        return self.turtles[name]

# --- Interpreter ---
class Interpreter:
    def __init__(self, name="<source>", turtle_mode="text"):
        self.name = name
        self.global_env = Environment()
        self.output_buffer = []
        self.turtles = TurtleManager(requested_mode=turtle_mode)
        self._install_builtins()

    def run(self, program):
        self._exec_stmts(program.statements, self.global_env)

    def run_string(self, source):
        toks = Lexer(source, "<repl>").tokenize()
        prog = Parser(toks, "<repl>").parse()
        self.run(prog)

    def _install_builtins(self):
        self._builtins = {
            "ask": self._builtin_ask,
            "number": self._builtin_number,
            "text": self._builtin_text,
            "random": self._builtin_random,
            "uppercase": self._builtin_uppercase,
            "lowercase": self._builtin_lowercase,
        }

    def _builtin_ask(self, args, loc):
        if len(args) != 1:
            raise TypeError_(f"`ask` takes exactly 1 argument, but I got {len(args)}.", loc)
        prompt = _to_text(args[0])
        try:
            return input(prompt)
        except EOFError:
            return ""

    def _builtin_number(self, args, loc):
        if len(args) != 1:
            raise TypeError_(f"`number` takes exactly 1 argument, but I got {len(args)}.", loc)
        return _to_number(args[0])

    def _builtin_text(self, args, loc):
        if len(args) != 1:
            raise TypeError_(f"`text` takes exactly 1 argument, but I got {len(args)}.", loc)
        return _to_text(args[0])

    def _builtin_random(self, args, loc):
        if len(args) != 2:
            raise TypeError_(f"`random` takes 2 arguments (low, high), but I got {len(args)}.", loc)
        lo = _to_number(args[0]); hi = _to_number(args[1])
        if lo > hi: lo, hi = hi, lo
        if isinstance(lo, int) and isinstance(hi, int):
            return _random.randint(int(lo), int(hi))
        return _random.uniform(lo, hi)

    def _builtin_uppercase(self, args, loc):
        if len(args) != 1:
            raise TypeError_(f"`uppercase` takes exactly 1 argument, but I got {len(args)}.", loc)
        if not isinstance(args[0], str):
            raise TypeError_(f"`uppercase` needs text, but I got {_typename(args[0])}.", loc)
        return args[0].upper()

    def _builtin_lowercase(self, args, loc):
        if len(args) != 1:
            raise TypeError_(f"`lowercase` takes exactly 1 argument, but I got {len(args)}.", loc)
        if not isinstance(args[0], str):
            raise TypeError_(f"`lowercase` needs text, but I got {_typename(args[0])}.", loc)
        return args[0].lower()

    def _exec_stmts(self, stmts, env):
        for s in stmts: self._exec(s, env)

    def _exec(self, stmt, env):
        method = self._DISPATCH.get(type(stmt))
        if method is None:
            raise RuntimeError_(f"I don't know how to run a {type(stmt).__name__}.", getattr(stmt, "location", None))
        method(self, stmt, env)

    def _exec_let(self, stmt, env):
        if isinstance(stmt.value, TurtleLiteral):
            t = self.turtles.create(stmt.name)
            env.define(stmt.name, t)
            return
        value = self._eval(stmt.value, env)
        env.define(stmt.name, value)

    def _exec_say(self, stmt, env):
        for part in stmt.parts:
            value = self._eval(part, env)
            text = _to_text(value)
            self.output_buffer.append(text)
            print(text)

    def _exec_if(self, stmt, env):
        if _to_bool(self._eval(stmt.condition, env)):
            self._exec_stmts(stmt.then_branch, env)
        elif stmt.else_branch is not None:
            self._exec_stmts(stmt.else_branch, env)

    def _exec_while(self, stmt, env):
        while _to_bool(self._eval(stmt.condition, env)):
            self._exec_stmts(stmt.body, env)

    def _exec_repeat(self, stmt, env):
        count = int(_to_number(self._eval(stmt.count, env)))
        if count < 0: count = 0
        for _ in range(count):
            self._exec_stmts(stmt.body, env)

    def _exec_for_each(self, stmt, env):
        iterable = self._eval(stmt.iterable, env)
        if not isinstance(iterable, list):
            raise TypeError_(f"I can only loop over a list, but I got {_typename(iterable)}.", stmt.iterable.location)
        for item in iterable:
            loop_env = env.child()
            loop_env.define(stmt.var_name, item)
            self._exec_stmts(stmt.body, loop_env)

    def _exec_function_def(self, stmt, env):
        env.define_function(stmt.name, stmt)

    def _exec_return(self, stmt, env):
        value = self._eval(stmt.value, env) if stmt.value is not None else None
        raise _ReturnSignal(value)

    def _exec_expr_stmt(self, stmt, env):
        self._eval(stmt.expression, env)

    def _exec_move(self, stmt, env):
        t = self.turtles.get(stmt.turtle_name)
        amount = _to_number(self._eval(stmt.amount, env))
        if stmt.direction == "forward": t.forward(amount)
        elif stmt.direction == "backward": t.backward(amount)
        elif stmt.direction == "left": t.left(amount)
        elif stmt.direction == "right": t.right(amount)

    def _exec_make(self, stmt, env):
        t = self.turtles.get(stmt.turtle_name)
        action = stmt.action
        if action == "hide": t.hide()
        elif action == "show": t.show()
        elif action == "pen_up": t.raise_pen()
        elif action == "pen_down": t.lower_pen()
        elif action == "erase_all": t.clear()
        elif action == "restart": t.reset()
        elif action == "home": t.home()
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
            if not isinstance(stmt.arg, ListLiteral) or len(stmt.arg.elements) != 2:
                raise RuntimeError_("'go to' needs two numbers.", stmt.location)
            x = _to_number(self._eval(stmt.arg.elements[0], env))
            y = _to_number(self._eval(stmt.arg.elements[1], env))
            t.goto_absolute(x, y)

    def _exec_goto(self, stmt, env):
        t = self.turtles.get(stmt.turtle_name)
        x_amount = _to_number(self._eval(stmt.x_amount, env))
        y_amount = _to_number(self._eval(stmt.y_amount, env))
        t.goto_relative(x_amount, stmt.x_dir, y_amount, stmt.y_dir)

    def _exec_set(self, stmt, env):
        t = self.turtles.get(stmt.turtle_name)
        prop = stmt.property
        value = self._eval(stmt.value, env)
        if prop == "pen color": t.set_pen_color(_to_text(value))
        elif prop == "pen size": t.set_pen_size(int(_to_number(value)))
        elif prop == "background": t.set_background(_to_text(value))

    _DISPATCH = {
        LetStatement: _exec_let, SayStatement: _exec_say, IfStatement: _exec_if,
        WhileStatement: _exec_while, RepeatStatement: _exec_repeat,
        ForEachStatement: _exec_for_each, FunctionDef: _exec_function_def,
        ReturnStatement: _exec_return, ExpressionStatement: _exec_expr_stmt,
        MoveStatement: _exec_move, MakeStatement: _exec_make,
        GotoStatement: _exec_goto, SetStatement: _exec_set,
    }

    def _eval(self, expr, env):
        if expr is None: return None
        method = self._EVAL_DISPATCH.get(type(expr))
        if method is None:
            raise RuntimeError_(f"I don't know how to evaluate a {type(expr).__name__}.", getattr(expr, "location", None))
        return method(self, expr, env)

    def _eval_number(self, e, env): return e.value
    def _eval_string(self, e, env): return e.value
    def _eval_bool(self, e, env): return e.value
    def _eval_nothing(self, e, env): return None

    def _eval_ident(self, e, env):
        try: return env.get(e.name)
        except KeyError:
            raise NameError_(f"I don't know what '{e.name}' means. Did you forget to define it with `let {e.name} be ...`?", e.location)

    def _eval_list(self, e, env):
        return [self._eval(x, env) for x in e.elements]

    def _eval_concat(self, e, env):
        return "".join(_to_text(self._eval(p, env)) for p in e.parts)

    def _eval_binary(self, e, env):
        op = e.op
        if op == "and":
            left = self._eval(e.left, env)
            if not _to_bool(left): return left
            return self._eval(e.right, env)
        if op == "or":
            left = self._eval(e.left, env)
            if _to_bool(left): return left
            return self._eval(e.right, env)
        left = self._eval(e.left, env)
        right = self._eval(e.right, env)
        if op == "plus": return _to_number(left) + _to_number(right)
        if op == "minus": return _to_number(left) - _to_number(right)
        if op == "times": return _to_number(left) * _to_number(right)
        if op == "divided by":
            rn = _to_number(right)
            if rn == 0: raise RuntimeError_("I can't divide by zero.", e.right.location)
            result = _to_number(left) / rn
            if isinstance(left, int) and isinstance(right, int) and isinstance(result, float) and result.is_integer():
                return int(result)
            return result
        if op == "mod":
            rn = _to_number(right)
            if rn == 0: raise RuntimeError_("I can't mod by zero.", e.right.location)
            return _to_number(left) % rn
        if op == "is": return left == right
        if op == "is not equal to": return left != right
        if op == "is greater than": return _to_number(left) > _to_number(right)
        if op == "is less than": return _to_number(left) < _to_number(right)
        if op == "is greater than or equal to": return _to_number(left) >= _to_number(right)
        if op == "is less than or equal to": return _to_number(left) <= _to_number(right)
        raise RuntimeError_(f"I don't know the operator '{op}'.", e.location)

    def _eval_unary(self, e, env):
        if e.op == "not": return not _to_bool(self._eval(e.operand, env))
        if e.op == "minus": return -_to_number(self._eval(e.operand, env))
        raise RuntimeError_(f"I don't know the operator '{e.op}'.", e.location)

    def _eval_index(self, e, env):
        coll = self._eval(e.collection, env)
        idx = int(_to_number(self._eval(e.index, env)))
        if not isinstance(coll, list):
            raise TypeError_(f"I can't use 'at' on {_typename(coll)}. `at` only works on lists.", e.location)
        if idx < 0: idx += len(coll)
        if idx < 0 or idx >= len(coll):
            raise RuntimeError_(f"I tried to get item {idx} from a list of size {len(coll)}.", e.index.location)
        return coll[idx]

    def _eval_size(self, e, env):
        coll = self._eval(e.collection, env)
        if isinstance(coll, (list, str)): return len(coll)
        raise TypeError_(f"I can't get the size of {_typename(coll)}.", e.location)

    def _eval_with_added(self, e, env):
        coll = self._eval(e.collection, env)
        if not isinstance(coll, list):
            raise TypeError_(f"I can only add to a list with 'with ... added'.", e.location)
        return coll + [self._eval(e.value, env)]

    def _eval_turtle_literal(self, e, env):
        return _turtle_factory_marker()

    def _eval_call(self, e, env):
        name = e.callee
        if (len(e.arguments) == 1 and isinstance(e.arguments[0], Identifier) and name in self.turtles.turtles):
            t = self.turtles.get(name)
            prop = e.arguments[0].name
            if prop == "heading": return t.heading
            if prop == "x": return t.x
            if prop == "y": return t.y
            raise RuntimeError_(f"I don't know what property '{prop}' means on a turtle.", e.location)
        args = [self._eval(a, env) for a in e.arguments]
        if name in self._builtins:
            return self._builtins[name](args, e.location)
        func = env.get_function(name)
        if func is None:
            raise NameError_(f"I don't know a function called '{name}'.", e.location)
        if len(func.params) != len(args):
            raise TypeError_(f"The function '{name}' expects {len(func.params)} argument(s) but I got {len(args)}.", e.location)
        call_env = env.child()
        for pname, pval in zip(func.params, args):
            call_env.define(pname, pval)
        try: self._exec_stmts(func.body, call_env)
        except _ReturnSignal as ret: return ret.value
        return None

    _EVAL_DISPATCH = {
        NumberLiteral: _eval_number, StringLiteral: _eval_string,
        BoolLiteral: _eval_bool, NothingLiteral: _eval_nothing,
        Identifier: _eval_ident, ListLiteral: _eval_list,
        ConcatExpression: _eval_concat, BinaryOp: _eval_binary,
        UnaryOp: _eval_unary, CallExpression: _eval_call,
        IndexExpression: _eval_index, SizeExpression: _eval_size,
        WithAddedExpression: _eval_with_added, TurtleLiteral: _eval_turtle_literal,
    }

# --- Web API ---
def run_e(source_code, input_func=None):
    """Run E source code and return (output, turtle_logs, error)."""
    import builtins
    original_input = builtins.input
    if input_func:
        builtins.input = input_func
    try:
        interp = Interpreter("<playground>", turtle_mode="text")
        interp.run_string(source_code)
        turtle_data = {}
        for name, t in interp.turtles.turtles.items():
            turtle_data[name] = {
                "log": t.log,
                "x": t.x, "y": t.y,
                "pen_color": t.pen_color,
                "pen_size": t.pen_size,
                "background": t.background,
                "visible": t.visible,
            }
        return interp.output_buffer, turtle_data, None
    except (LexerError, ParseError, RuntimeError_, NameError_, TypeError_) as e:
        return [], {}, e.format()
    except Exception as e:
        return [], {}, f"E Error: {e}"
    finally:
        builtins.input = original_input
