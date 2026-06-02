"""Rigorous tests for the E Parser."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest

from src.lexer import Lexer
from src.parser import Parser
from src.tokens import TokenType
from src.ast_nodes import (
    Program, LetStatement, SayStatement, IfStatement, WhileStatement,
    RepeatStatement, ForEachStatement, FunctionDef, ReturnStatement,
    ExpressionStatement,
    NumberLiteral, StringLiteral, BoolLiteral, NothingLiteral, Identifier,
    ListLiteral, ConcatExpression, BinaryOp, UnaryOp, CallExpression,
    IndexExpression, SizeExpression, WithAddedExpression,
)


def parse(src: str) -> Program:
    """Helper: lex + parse a source string."""
    toks = Lexer(src, "<test>").tokenize()
    return Parser(toks, "<test>").parse()


def first(p: Program):
    """Return the first statement of the program."""
    assert p.statements, f"Expected at least one statement, got 0"
    return p.statements[0]


class TestParserBasics(unittest.TestCase):
    def test_empty_program(self):
        p = parse("")
        self.assertEqual(p.statements, [])

    def test_whitespace_only(self):
        p = parse("   \n  \n")
        self.assertEqual(p.statements, [])

    def test_say_string(self):
        p = parse('say "hello"')
        stmt = first(p)
        self.assertIsInstance(stmt, SayStatement)
        self.assertEqual(len(stmt.parts), 1)
        self.assertIsInstance(stmt.parts[0], StringLiteral)
        self.assertEqual(stmt.parts[0].value, "hello")

    def test_say_concat(self):
        p = parse('say "Hello, " , name')
        stmt = first(p)
        self.assertIsInstance(stmt, SayStatement)
        self.assertEqual(len(stmt.parts), 1)
        concat = stmt.parts[0]
        self.assertIsInstance(concat, ConcatExpression)
        self.assertEqual(len(concat.parts), 2)
        self.assertIsInstance(concat.parts[0], StringLiteral)
        self.assertIsInstance(concat.parts[1], Identifier)

    def test_let_number(self):
        p = parse("let x be 5")
        stmt = first(p)
        self.assertIsInstance(stmt, LetStatement)
        self.assertEqual(stmt.name, "x")
        self.assertIsInstance(stmt.value, NumberLiteral)
        self.assertEqual(stmt.value.value, 5)

    def test_let_string(self):
        p = parse('let name be "Alice"')
        stmt = first(p)
        self.assertIsInstance(stmt, LetStatement)
        self.assertEqual(stmt.name, "name")
        self.assertIsInstance(stmt.value, StringLiteral)

    def test_let_true(self):
        p = parse("let x be true")
        stmt = first(p)
        self.assertIsInstance(stmt, LetStatement)
        self.assertIsInstance(stmt.value, BoolLiteral)
        self.assertTrue(stmt.value.value)

    def test_let_nothing(self):
        p = parse("let x be nothing")
        stmt = first(p)
        self.assertIsInstance(stmt, LetStatement)
        self.assertIsInstance(stmt.value, NothingLiteral)


class TestParserExpressions(unittest.TestCase):
    def test_primary_number(self):
        p = parse("say 5")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, NumberLiteral)
        self.assertEqual(expr.value, 5)

    def test_primary_string(self):
        p = parse('say "hi"')
        expr = first(p).parts[0]
        self.assertIsInstance(expr, StringLiteral)

    def test_primary_bool(self):
        p = parse("say true")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, BoolLiteral)
        self.assertTrue(expr.value)

    def test_primary_identifier(self):
        p = parse("say x")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, Identifier)
        self.assertEqual(expr.name, "x")

    def test_addition(self):
        p = parse("say 3 plus 4")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "plus")
        self.assertEqual(expr.left.value, 3)
        self.assertEqual(expr.right.value, 4)

    def test_subtraction(self):
        p = parse("say 10 minus 3")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "minus")

    def test_multiplication(self):
        p = parse("say 5 times 2")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "times")

    def test_division(self):
        p = parse("say 10 divided by 2")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "divided by")

    def test_modulo(self):
        p = parse("say 10 mod 3")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "mod")

    def test_precedence_mul_over_add(self):
        # 2 plus 3 times 4 = 2 + (3*4) = 14
        p = parse("say 2 plus 3 times 4")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "plus")
        self.assertEqual(expr.left.value, 2)
        self.assertIsInstance(expr.right, BinaryOp)
        self.assertEqual(expr.right.op, "times")
        self.assertEqual(expr.right.left.value, 3)
        self.assertEqual(expr.right.right.value, 4)

    def test_precedence_parens(self):
        # (2 plus 3) times 4 = 20
        p = parse("say (2 plus 3) times 4")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "times")
        self.assertIsInstance(expr.left, BinaryOp)
        self.assertEqual(expr.left.op, "plus")
        self.assertEqual(expr.right.value, 4)

    def test_unary_minus(self):
        # `-5` is a single negative number literal in the lexer.
        p = parse("say -5")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, NumberLiteral)
        self.assertEqual(expr.value, -5)

    def test_unary_minus_keyword(self):
        # `minus` is the keyword form: produces an explicit UnaryOp.
        p = parse("say minus 5")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, UnaryOp)
        self.assertEqual(expr.op, "minus")
        self.assertEqual(expr.operand.value, 5)

    def test_unary_minus_in_expr(self):
        # 5 - -3 = 8; the lexer folds the inner `-3` into a negative number.
        p = parse("say 5 - -3")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "minus")
        self.assertEqual(expr.left.value, 5)
        self.assertIsInstance(expr.right, NumberLiteral)
        self.assertEqual(expr.right.value, -3)

    def test_not(self):
        p = parse("say not true")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, UnaryOp)
        self.assertEqual(expr.op, "not")

    def test_and(self):
        p = parse("say true and false")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "and")

    def test_or(self):
        p = parse("say true or false")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "or")

    def test_and_higher_than_or(self):
        # true or false and false = true or (false and false) = true or false = true
        p = parse("say true or false and false")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "or")
        self.assertIsInstance(expr.right, BinaryOp)
        self.assertEqual(expr.right.op, "and")

    def test_not_higher_than_and(self):
        # not true and false = (not true) and false = false
        p = parse("say not true and false")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "and")
        self.assertIsInstance(expr.left, UnaryOp)
        self.assertEqual(expr.left.op, "not")


class TestParserComparisons(unittest.TestCase):
    def test_is(self):
        p = parse("say x is 5")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "is")

    def test_is_equal_to(self):
        p = parse("say x is equal to 5")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "is")

    def test_is_not_equal_to(self):
        p = parse("say x is not equal to 5")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "is not equal to")

    def test_is_greater_than(self):
        p = parse("say x is greater than 5")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "is greater than")

    def test_is_less_than(self):
        p = parse("say x is less than 5")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "is less than")

    def test_is_greater_or_equal(self):
        p = parse("say x is greater than or equal to 5")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "is greater than or equal to")

    def test_is_less_or_equal(self):
        p = parse("say x is less than or equal to 5")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, BinaryOp)
        self.assertEqual(expr.op, "is less than or equal to")


class TestParserLists(unittest.TestCase):
    def test_empty_list(self):
        p = parse("say []")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, ListLiteral)
        self.assertEqual(expr.elements, [])

    def test_list_of_numbers(self):
        p = parse("say [1, 2, 3]")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, ListLiteral)
        self.assertEqual(len(expr.elements), 3)
        self.assertEqual([e.value for e in expr.elements], [1, 2, 3])

    def test_list_of_strings(self):
        p = parse('say ["a", "b"]')
        expr = first(p).parts[0]
        self.assertIsInstance(expr, ListLiteral)
        self.assertEqual([e.value for e in expr.elements], ["a", "b"])

    def test_list_in_let(self):
        p = parse("let nums be [1, 2, 3]")
        stmt = first(p)
        self.assertIsInstance(stmt, LetStatement)
        self.assertIsInstance(stmt.value, ListLiteral)

    def test_index_expression(self):
        p = parse("say nums at 0")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, IndexExpression)
        self.assertIsInstance(expr.collection, Identifier)
        self.assertEqual(expr.index.value, 0)

    def test_size_of(self):
        p = parse("say size of nums")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, SizeExpression)
        self.assertIsInstance(expr.collection, Identifier)

    def test_with_added(self):
        p = parse("say nums with 6 added")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, WithAddedExpression)


class TestParserFunctionCalls(unittest.TestCase):
    def test_no_args(self):
        p = parse("greet")
        # 'greet' alone is just an identifier (no call)
        stmt = first(p)
        self.assertIsInstance(stmt, ExpressionStatement)
        self.assertIsInstance(stmt.expression, Identifier)

    def test_one_arg(self):
        p = parse('greet "Alice"')
        stmt = first(p)
        self.assertIsInstance(stmt, ExpressionStatement)
        self.assertIsInstance(stmt.expression, CallExpression)
        self.assertEqual(stmt.expression.callee, "greet")
        self.assertEqual(len(stmt.expression.arguments), 1)
        self.assertIsInstance(stmt.expression.arguments[0], StringLiteral)

    def test_multiple_args(self):
        p = parse("add 3, 4")
        stmt = first(p)
        self.assertIsInstance(stmt, ExpressionStatement)
        self.assertIsInstance(stmt.expression, CallExpression)
        self.assertEqual(stmt.expression.callee, "add")
        self.assertEqual(len(stmt.expression.arguments), 2)
        self.assertEqual(stmt.expression.arguments[0].value, 3)
        self.assertEqual(stmt.expression.arguments[1].value, 4)

    def test_ask_call(self):
        p = parse('let name be ask "What is your name? "')
        stmt = first(p)
        self.assertIsInstance(stmt, LetStatement)
        self.assertIsInstance(stmt.value, CallExpression)
        self.assertEqual(stmt.value.callee, "ask")
        self.assertIsInstance(stmt.value.arguments[0], StringLiteral)

    def test_say_with_call(self):
        p = parse("say greet name")
        expr = first(p).parts[0]
        self.assertIsInstance(expr, CallExpression)
        self.assertEqual(expr.callee, "greet")
        self.assertEqual(len(expr.arguments), 1)
        self.assertIsInstance(expr.arguments[0], Identifier)


class TestParserControlFlow(unittest.TestCase):
    def test_if(self):
        p = parse("if x is 5 then\n    say \"yes\"\nend")
        stmt = first(p)
        self.assertIsInstance(stmt, IfStatement)
        self.assertIsInstance(stmt.condition, BinaryOp)
        self.assertEqual(len(stmt.then_branch), 1)
        self.assertIsNone(stmt.else_branch)

    def test_if_else(self):
        p = parse("if x is 5 then\n    say \"yes\"\nelse\n    say \"no\"\nend")
        stmt = first(p)
        self.assertIsInstance(stmt, IfStatement)
        self.assertEqual(len(stmt.then_branch), 1)
        self.assertIsNotNone(stmt.else_branch)
        self.assertEqual(len(stmt.else_branch), 1)

    def test_while(self):
        p = parse("while i is less than 10\n    say i\nend")
        stmt = first(p)
        self.assertIsInstance(stmt, WhileStatement)
        self.assertEqual(len(stmt.body), 1)

    def test_else_if_chain(self):
        # `else if` chain shares a single `end`
        p = parse("""
if x is 1 then
    say "one"
else if x is 2 then
    say "two"
else if x is 3 then
    say "three"
else
    say "other"
end
""")
        stmt = first(p)
        self.assertIsInstance(stmt, IfStatement)
        self.assertIsNotNone(stmt.else_branch)
        self.assertEqual(len(stmt.else_branch), 1)
        inner = stmt.else_branch[0]
        self.assertIsInstance(inner, IfStatement)
        self.assertIsNotNone(inner.else_branch)
        self.assertEqual(len(inner.else_branch), 1)
        inner2 = inner.else_branch[0]
        self.assertIsInstance(inner2, IfStatement)
        self.assertIsNotNone(inner2.else_branch)
        # The deepest else is a regular block with a say statement
        self.assertEqual(len(inner2.else_branch), 1)
        self.assertIsInstance(inner2.else_branch[0], SayStatement)

    def test_repeat(self):
        p = parse("repeat 5 times\n    say \"hi\"\nend")
        stmt = first(p)
        self.assertIsInstance(stmt, RepeatStatement)
        self.assertEqual(stmt.count.value, 5)
        self.assertEqual(len(stmt.body), 1)

    def test_for_each(self):
        p = parse("for each fruit in fruits\n    say fruit\nend")
        stmt = first(p)
        self.assertIsInstance(stmt, ForEachStatement)
        self.assertEqual(stmt.var_name, "fruit")
        self.assertIsInstance(stmt.iterable, Identifier)
        self.assertEqual(len(stmt.body), 1)


class TestParserFunctions(unittest.TestCase):
    def test_function_def(self):
        p = parse("to greet name\n    say \"Hello, \" , name\nend")
        stmt = first(p)
        self.assertIsInstance(stmt, FunctionDef)
        self.assertEqual(stmt.name, "greet")
        self.assertEqual(stmt.params, ["name"])
        self.assertEqual(len(stmt.body), 1)

    def test_function_def_no_params_fails(self):
        from src.errors import ParseError
        with self.assertRaises(ParseError):
            parse("to doSomething\n    say x\nend")

    def test_function_def_multiple_params(self):
        p = parse("to add a b c\n    return a\nend")
        stmt = first(p)
        self.assertEqual(stmt.params, ["a", "b", "c"])

    def test_return_with_value(self):
        p = parse("to square x\n    return x times x\nend")
        # First stmt: FunctionDef, second: ReturnStatement
        self.assertEqual(len(p.statements), 1)
        func = p.statements[0]
        self.assertIsInstance(func, FunctionDef)
        ret = func.body[0]
        self.assertIsInstance(ret, ReturnStatement)
        self.assertIsInstance(ret.value, BinaryOp)

    def test_return_without_value(self):
        p = parse("to f param\n    return\nend")
        func = first(p)
        ret = func.body[0]
        self.assertIsInstance(ret, ReturnStatement)
        self.assertIsNone(ret.value)


class TestParserPrograms(unittest.TestCase):
    def test_full_program(self):
        src = """
        -- a complete program
        let name be "Alice"
        let age be 30

        say "Hello, " , name

        if age is greater than 18 then
            say "adult"
        else
            say "minor"
        end

        repeat 3 times
            say "hi"
        end
        """
        p = parse(src)
        self.assertEqual(len(p.statements), 5)
        self.assertIsInstance(p.statements[0], LetStatement)
        self.assertIsInstance(p.statements[1], LetStatement)
        self.assertIsInstance(p.statements[2], SayStatement)
        self.assertIsInstance(p.statements[3], IfStatement)
        self.assertIsInstance(p.statements[4], RepeatStatement)


class TestParserErrors(unittest.TestCase):
    def test_missing_be(self):
        from src.errors import ParseError
        with self.assertRaises(ParseError):
            parse("let x 5")

    def test_missing_end_in_if(self):
        from src.errors import ParseError
        with self.assertRaises(ParseError):
            parse("if x is 5 then\n    say \"hi\"")

    def test_let_without_name(self):
        from src.errors import ParseError
        with self.assertRaises(ParseError):
            parse("let be 5")

    def test_repeat_without_times(self):
        from src.errors import ParseError
        with self.assertRaises(ParseError):
            parse("repeat 5\n    say x\nend")


if __name__ == "__main__":
    unittest.main(verbosity=2)
