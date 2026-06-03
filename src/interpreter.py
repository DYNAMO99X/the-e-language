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
