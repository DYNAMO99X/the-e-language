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
