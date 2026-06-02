"""Rigorous tests for the E Lexer.

Run with:  python -m pytest tests/test_lexer.py -v
or:        python tests/test_lexer.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest

from src.lexer import Lexer
from src.tokens import TokenType


def lex(src: str):
    """Helper: lex `src` and return a list of (type, value) pairs, ignoring NEWLINEs and EOF."""
    toks = Lexer(src, "<test>").tokenize()
    return [(t.type, t.value) for t in toks if t.type not in (TokenType.NEWLINE, TokenType.EOF)]


class TestLexerBasics(unittest.TestCase):
    def test_empty_source(self):
        self.assertEqual(lex(""), [])

    def test_whitespace_only(self):
        self.assertEqual(lex("   \t  "), [])

    def test_single_keyword_let(self):
        self.assertEqual(lex("let"), [(TokenType.LET, "let")])

    def test_case_insensitive_let(self):
        self.assertEqual(lex("LET Let LeT"), [
            (TokenType.LET, "LET"),
            (TokenType.LET, "Let"),
            (TokenType.LET, "LeT"),
        ])

    def test_identifier(self):
        self.assertEqual(lex("x"), [(TokenType.IDENT, "x")])
        self.assertEqual(lex("my_var"), [(TokenType.IDENT, "my_var")])
        self.assertEqual(lex("hello123"), [(TokenType.IDENT, "hello123")])
        self.assertEqual(lex("_private"), [(TokenType.IDENT, "_private")])

    def test_keywords(self):
        for kw, ttype in [
            ("let", TokenType.LET), ("be", TokenType.BE), ("say", TokenType.SAY),
            ("ask", TokenType.ASK), ("if", TokenType.IF), ("then", TokenType.THEN),
            ("else", TokenType.ELSE), ("end", TokenType.END), ("while", TokenType.WHILE),
            ("repeat", TokenType.REPEAT), ("times", TokenType.TIMES),
            ("for", TokenType.FOR), ("each", TokenType.EACH), ("in", TokenType.IN),
            ("to", TokenType.TO), ("return", TokenType.RETURN),
            ("true", TokenType.TRUE), ("false", TokenType.FALSE),
            ("nothing", TokenType.NOTHING),
        ]:
            with self.subTest(kw=kw):
                self.assertEqual(lex(kw), [(ttype, kw)])

    def test_math_keywords(self):
        self.assertEqual(lex("plus"), [(TokenType.PLUS, "plus")])
        self.assertEqual(lex("minus"), [(TokenType.MINUS, "minus")])
        self.assertEqual(lex("times"), [(TokenType.TIMES, "times")])
        self.assertEqual(lex("mod"), [(TokenType.MOD, "mod")])
        self.assertEqual(lex("divided by"), [(TokenType.DIVIDED, "divided by")])
        self.assertEqual(lex("at"), [(TokenType.AT, "at")])
        self.assertEqual(lex("with"), [(TokenType.WITH, "with")])
        self.assertEqual(lex("added"), [(TokenType.ADDED, "added")])
        self.assertEqual(lex("size"), [(TokenType.SIZE, "size")])
        self.assertEqual(lex("of"), [(TokenType.OF, "of")])
        self.assertEqual(lex("size of"),
                         [(TokenType.SIZE, "size"), (TokenType.OF, "of")])

    def test_comparison_keywords(self):
        self.assertEqual(lex("is"), [(TokenType.IS, "is")])
        self.assertEqual(lex("is equal to"), [(TokenType.IS, "is equal to")])
        self.assertEqual(lex("is not equal to"), [(TokenType.IS_NOT_EQUAL, "is not equal to")])
        self.assertEqual(lex("is greater than"), [(TokenType.IS_GREATER, "is greater than")])
        self.assertEqual(lex("is less than"), [(TokenType.IS_LESS, "is less than")])
        self.assertEqual(lex("is greater than or equal to"),
                         [(TokenType.IS_GREATER_EQ, "is greater than or equal to")])
        self.assertEqual(lex("is less than or equal to"),
                         [(TokenType.IS_LESS_EQ, "is less than or equal to")])

    def test_comparison_prefers_longest(self):
        # "is greater than" should NOT match "is greater than or equal to"
        toks = lex("is greater than x")
        self.assertEqual(toks[0][0], TokenType.IS_GREATER)
        self.assertEqual(toks[1], (TokenType.IDENT, "x"))


class TestLexerNumbers(unittest.TestCase):
    def test_integer(self):
        self.assertEqual(lex("5"), [(TokenType.NUMBER, 5)])
        self.assertEqual(lex("0"), [(TokenType.NUMBER, 0)])
        self.assertEqual(lex("12345"), [(TokenType.NUMBER, 12345)])

    def test_decimal(self):
        self.assertEqual(lex("3.14"), [(TokenType.NUMBER, 3.14)])
        self.assertEqual(lex("0.5"), [(TokenType.NUMBER, 0.5)])

    def test_negative_number_at_start(self):
        # At the start of a line/after newline, `-5` is a negative number
        self.assertEqual(lex("-5"), [(TokenType.NUMBER, -5)])
        self.assertEqual(lex("\n-5"), [(TokenType.NUMBER, -5)])

    def test_negative_in_expression(self):
        # After `=` style or operator, `-5` is a negative number.
        # In our case, after a NEWLINE it's a negative.
        toks = lex("let x be\n-5")
        # find the number token
        nums = [v for t, v in toks if t == TokenType.NUMBER]
        self.assertEqual(nums, [-5])

    def test_minus_after_value(self):
        # After a value, `-` is the binary minus operator
        toks = lex("5 - 3")
        self.assertEqual(toks, [
            (TokenType.NUMBER, 5),
            (TokenType.MINUS, "-"),
            (TokenType.NUMBER, 3),
        ])


class TestLexerStrings(unittest.TestCase):
    def test_simple_string(self):
        self.assertEqual(lex('"hello"'), [(TokenType.STRING, "hello")])

    def test_empty_string(self):
        self.assertEqual(lex('""'), [(TokenType.STRING, "")])

    def test_string_with_spaces(self):
        self.assertEqual(lex('"hello world"'), [(TokenType.STRING, "hello world")])

    def test_string_with_escapes(self):
        self.assertEqual(lex(r'"a\nb"'), [(TokenType.STRING, "a\nb")])
        self.assertEqual(lex(r'"say \"hi\""'), [(TokenType.STRING, 'say "hi"')])
        self.assertEqual(lex(r'"a\\b"'), [(TokenType.STRING, "a\\b")])

    def test_unterminated_string_raises(self):
        from src.errors import LexerError
        with self.assertRaises(LexerError):
            Lexer('"oops', "<test>").tokenize()


class TestLexerAlternativeQuotes(unittest.TestCase):
    """Tests for `'` and `` ` `` as alternative string delimiters."""

    def test_single_quote_string(self):
        self.assertEqual(lex("'hello'"), [(TokenType.STRING, "hello")])

    def test_backtick_string(self):
        self.assertEqual(lex("`hello`"), [(TokenType.STRING, "hello")])

    def test_empty_single_quote(self):
        self.assertEqual(lex("''"), [(TokenType.STRING, "")])

    def test_empty_backtick(self):
        self.assertEqual(lex("``"), [(TokenType.STRING, "")])

    def test_apostrophe_escape_in_single_quote(self):
        # 'don\'t' -> "don't"
        self.assertEqual(lex(r"'don\'t'"), [(TokenType.STRING, "don't")])

    def test_backtick_escape_in_backtick(self):
        # `back\`tick` -> "back`tick"
        self.assertEqual(lex(r"`back\`tick`"), [(TokenType.STRING, "back`tick")])

    def test_cross_quote_escape_single_in_double(self):
        # "don\'t" -> "don't"
        self.assertEqual(lex(r'"don\'t"'), [(TokenType.STRING, "don't")])

    def test_cross_quote_escape_double_in_single(self):
        # Source: 'say \"hi\"' — escaped double quotes work inside single quotes.
        self.assertEqual(lex('\'say \\"hi\\"\''),
                         [(TokenType.STRING, 'say "hi"')])

    def test_cross_quote_escape_backtick_in_double(self):
        self.assertEqual(lex(r'"a\`b"'), [(TokenType.STRING, "a`b")])

    def test_all_standard_escapes_in_single_quote(self):
        self.assertEqual(lex(r"'\n\t\\'"), [(TokenType.STRING, "\n\t\\")])

    def test_all_standard_escapes_in_backtick(self):
        self.assertEqual(lex(r"`\n\t\\`"), [(TokenType.STRING, "\n\t\\")])

    def test_unterminated_single_quote_raises(self):
        from src.errors import LexerError
        with self.assertRaises(LexerError):
            Lexer("'oops", "<test>").tokenize()

    def test_unterminated_backtick_raises(self):
        from src.errors import LexerError
        with self.assertRaises(LexerError):
            Lexer("`oops", "<test>").tokenize()

    def test_unterminated_error_mentions_quote(self):
        from src.errors import LexerError
        try:
            Lexer("'no end", "<test>").tokenize()
            self.fail("expected LexerError")
        except LexerError as e:
            self.assertIn("'", e.message)

    def test_mixed_quote_types_in_program(self):
        # All three kinds in one expression list
        self.assertEqual(
            lex('"a", \'b\', `c`'),
            [(TokenType.STRING, "a"), (TokenType.COMMA, ","),
             (TokenType.STRING, "b"), (TokenType.COMMA, ","),
             (TokenType.STRING, "c")],
        )

    def test_quote_chars_in_value(self):
        # The actual quote character shows up in the string value when escaped
        self.assertEqual(lex(r"'a\"b'"), [(TokenType.STRING, 'a"b')])
        self.assertEqual(lex(r'`a\'b`'), [(TokenType.STRING, "a'b")])
        self.assertEqual(lex(r'"a\`b"'), [(TokenType.STRING, "a`b")])

    def test_string_with_spaces_in_single_quote(self):
        self.assertEqual(lex("'hello world'"), [(TokenType.STRING, "hello world")])

    def test_string_with_spaces_in_backtick(self):
        self.assertEqual(lex("`hello world`"), [(TokenType.STRING, "hello world")])


class TestLexerSymbols(unittest.TestCase):
    def test_comma(self):
        self.assertEqual(lex(","), [(TokenType.COMMA, ",")])
    def test_parens(self):
        self.assertEqual(lex("()"), [(TokenType.LPAREN, "("), (TokenType.RPAREN, ")")])
    def test_brackets(self):
        self.assertEqual(lex("[]"), [(TokenType.LBRACKET, "["), (TokenType.RBRACKET, "]")])

    def test_unknown_char_raises(self):
        from src.errors import LexerError
        with self.assertRaises(LexerError):
            Lexer("@", "<test>").tokenize()


class TestLexerComments(unittest.TestCase):
    def test_line_comment_skipped(self):
        self.assertEqual(lex("-- this is a comment\nsay x"),
                         [(TokenType.SAY, "say"), (TokenType.IDENT, "x")])

    def test_inline_comment(self):
        self.assertEqual(lex('say "hi" -- greet the user'),
                         [(TokenType.SAY, "say"), (TokenType.STRING, "hi")])

    def test_comment_at_end(self):
        self.assertEqual(lex("let x be 5 --"), [(TokenType.LET, "let"), (TokenType.IDENT, "x"),
                                                (TokenType.BE, "be"), (TokenType.NUMBER, 5)])


class TestLexerPrograms(unittest.TestCase):
    def test_hello_world(self):
        toks = lex('say "Hello, world!"')
        self.assertEqual(toks, [(TokenType.SAY, "say"), (TokenType.STRING, "Hello, world!")])

    def test_let_statement(self):
        toks = lex("let x be 5")
        self.assertEqual(toks, [
            (TokenType.LET, "let"), (TokenType.IDENT, "x"),
            (TokenType.BE, "be"), (TokenType.NUMBER, 5),
        ])

    def test_say_with_concat(self):
        toks = lex('say "Hello, " , name')
        self.assertEqual(toks, [
            (TokenType.SAY, "say"),
            (TokenType.STRING, "Hello, "),
            (TokenType.COMMA, ","),
            (TokenType.IDENT, "name"),
        ])

    def test_if_statement(self):
        toks = lex("if x is greater than 10 then\n    say \"big\"\nelse\n    say \"small\"\nend")
        # Just check key tokens
        types = [t for t, _ in toks]
        self.assertIn(TokenType.IF, types)
        self.assertIn(TokenType.IS_GREATER, types)
        self.assertIn(TokenType.THEN, types)
        self.assertIn(TokenType.ELSE, types)
        self.assertIn(TokenType.END, types)
        self.assertIn(TokenType.SAY, types)

    def test_while_loop(self):
        toks = lex("while i is less than 10\n    say i\n    let i be i plus 1\nend")
        types = [t for t, _ in toks]
        self.assertIn(TokenType.WHILE, types)
        self.assertIn(TokenType.IS_LESS, types)
        self.assertIn(TokenType.END, types)

    def test_repeat_loop(self):
        toks = lex("repeat 5 times\n    say \"hi\"\nend")
        types = [t for t, _ in toks]
        self.assertIn(TokenType.REPEAT, types)
        self.assertIn(TokenType.TIMES, types)
        self.assertIn(TokenType.END, types)

    def test_function_def(self):
        toks = lex("to greet name\n    say \"Hello, \" , name\nend")
        types = [t for t, _ in toks]
        self.assertIn(TokenType.TO, types)
        self.assertIn(TokenType.END, types)

    def test_list_literal(self):
        toks = lex("let nums be [1, 2, 3]")
        self.assertEqual(toks, [
            (TokenType.LET, "let"), (TokenType.IDENT, "nums"), (TokenType.BE, "be"),
            (TokenType.LBRACKET, "["), (TokenType.NUMBER, 1), (TokenType.COMMA, ","),
            (TokenType.NUMBER, 2), (TokenType.COMMA, ","), (TokenType.NUMBER, 3),
            (TokenType.RBRACKET, "]"),
        ])


class TestLexerLineNumbers(unittest.TestCase):
    def test_line_tracking(self):
        toks = Lexer("say 1\nsay 2\nsay 3", "<t>").tokenize()
        # find the NUMBER tokens
        num_toks = [t for t in toks if t.type == TokenType.NUMBER]
        self.assertEqual([t.location.line for t in num_toks], [1, 2, 3])

    def test_error_includes_line(self):
        from src.errors import LexerError
        try:
            Lexer('say "oops\nsay 2', "<t>").tokenize()
            self.fail("expected LexerError")
        except LexerError as e:
            self.assertIn("1", e.message)


if __name__ == "__main__":
    unittest.main(verbosity=2)
