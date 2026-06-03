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
    ShowWindow, HideWindow, TextOf, TimeoutValuePair,
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
    # Web / JSON multi-word function names
    TokenType.STATUS_OF,  # 'status of resp'
    TokenType.BODY_OF,    # 'body of resp'
    TokenType.JSON_OF,    # 'json of resp'
    TokenType.JSON_PARSE, # 'json parse text'
    TokenType.JSON_KEYS,  # 'json keys obj'
    TokenType.JSON_VALUE, # 'json value obj, key'
    TokenType.TIMEOUT,    # 'timeout 5' in get/post calls
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

    def _parse_primary(self, allow_call: bool = True) -> Optional[object]:
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
            return self._parse_ident_or_call(allow_call=allow_call)
        if tok.type == TokenType.TIMEOUT:
            # 'timeout' in `get "url", timeout 5` — treat as string "timeout"
            self._advance()
            return StringLiteral(value="timeout", location=tok.location)
        if tok.type == TokenType.ASK:
            return self._parse_ask()
        # Web / JSON multi-word function names
        if tok.type in (TokenType.STATUS_OF, TokenType.BODY_OF,
                        TokenType.JSON_OF, TokenType.JSON_PARSE,
                        TokenType.JSON_KEYS, TokenType.JSON_VALUE):
            return self._parse_web_call()

        return None

    def _parse_ask(self) -> object:
        ask_tok = self._advance()  # ASK
        prompt = self._parse_expression()
        if prompt is None:
            raise self._error("After 'ask' I expected a prompt string")
        return CallExpression(callee="ask", arguments=[prompt], location=ask_tok.location)

    def _parse_web_call(self) -> object:
        """Parse multi-word web/JSON function calls.

        Handles: status of, body of, json of, json parse, json keys, json value
        The multi-word token is already consumed; we parse the arguments.
        """
        tok = self._advance()  # consume the multi-word token
        callee_map = {
            TokenType.STATUS_OF: "status of",
            TokenType.BODY_OF: "body of",
            TokenType.JSON_OF: "json of",
            TokenType.JSON_PARSE: "json parse",
            TokenType.JSON_KEYS: "json keys",
            TokenType.JSON_VALUE: "json value",
        }
        callee = callee_map[tok.type]

        # Parse arguments: single value, or two values separated by comma
        first = self._parse_call_arg()
        if first is None:
            raise self._error(f"After '{callee}' I expected an argument")
        args = [first]
        if self._check(TokenType.COMMA):
            self._advance()
            second = self._parse_call_arg()
            if second is None:
                raise self._error(f"After ',' in '{callee}' I expected a second argument")
            args.append(second)

        return CallExpression(callee=callee, arguments=args, location=tok.location)

    def _parse_ident_or_call(self, allow_call: bool = True) -> object:
        name_tok = self._advance()  # IDENT
        # Look ahead: if the next token starts an expression, this is a call.
        if allow_call and self._peek().type in _EXPR_START:
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
        expr = self._parse_primary(allow_call=False)
        if expr is None:
            return None
        # Special case: `timeout <value>` in get/post calls.
        # The TIMEOUT keyword is parsed as StringLiteral("timeout") by
        # _parse_primary.  Consume the next primary as the timeout value
        # and return a TimeoutValuePair so the interpreter can unpack it.
        if (isinstance(expr, StringLiteral) and expr.value == "timeout"
                and self._peek().type in _EXPR_START):
            value = self._parse_primary(allow_call=False)
            if value is not None:
                return TimeoutValuePair(
                    keyword="timeout",
                    value=value,
                    location=expr.location,
                )
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
