"""Rigorous tests for the E Interpreter."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import io
import unittest
from contextlib import redirect_stdout

from src.interpreter import Interpreter
from src.errors import EError


def run(src: str, stdin: str = "") -> str:
    """Run E source, feed stdin if needed, return captured stdout."""
    interp = Interpreter("<test>")
    # Capture stdin by monkey-patching input
    if stdin:
        import builtins
        original = builtins.input
        inputs = iter(stdin.split("\n"))
        builtins.input = lambda prompt="": next(inputs)
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            interp.run_string(src)
    finally:
        if stdin:
            builtins.input = original
    return buf.getvalue()


class TestInterpreterBasics(unittest.TestCase):
    def test_say_string(self):
        self.assertEqual(run('say "hello"'), "hello\n")

    def test_say_number(self):
        self.assertEqual(run("say 5"), "5\n")

    def test_say_concat(self):
        self.assertEqual(run('say "Hello, " , "world"'), "Hello, world\n")

    def test_say_concat_with_var(self):
        src = '''
        let name be "Alice"
        say "Hello, " , name
        '''
        self.assertEqual(run(src), "Hello, Alice\n")

    def test_let_and_say(self):
        src = '''
        let x be 5
        let y be 10
        say x
        say y
        '''
        self.assertEqual(run(src), "5\n10\n")

    def test_multiple_say(self):
        self.assertEqual(run('say "a"\nsay "b"'), "a\nb\n")

    def test_say_true(self):
        self.assertEqual(run("say true"), "true\n")
        self.assertEqual(run("say false"), "false\n")

    def test_say_nothing(self):
        self.assertEqual(run("say nothing"), "nothing\n")


class TestInterpreterMath(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(run("say 3 plus 4"), "7\n")

    def test_subtraction(self):
        self.assertEqual(run("say 10 minus 3"), "7\n")

    def test_multiplication(self):
        self.assertEqual(run("say 5 times 3"), "15\n")

    def test_division(self):
        self.assertEqual(run("say 10 divided by 2"), "5\n")

    def test_division_decimal(self):
        self.assertEqual(run("say 10 divided by 4"), "2.5\n")

    def test_modulo(self):
        self.assertEqual(run("say 10 mod 3"), "1\n")

    def test_precedence(self):
        # 2 + 3*4 = 14
        self.assertEqual(run("say 2 plus 3 times 4"), "14\n")
        # (2+3)*4 = 20
        self.assertEqual(run("say (2 plus 3) times 4"), "20\n")

    def test_negative_number(self):
        self.assertEqual(run("say -5"), "-5\n")

    def test_unary_minus_keyword(self):
        self.assertEqual(run("let x be 5\nsay minus x"), "-5\n")

    def test_divide_by_zero(self):
        from src.errors import RuntimeError_
        with self.assertRaises(RuntimeError_):
            run("say 5 divided by 0")

    def test_complex_expression(self):
        src = "say (10 plus 5) times 2 minus 8"
        self.assertEqual(run(src), "22\n")  # (15 * 2) - 8 = 22


class TestInterpreterComparisons(unittest.TestCase):
    def test_is_equal(self):
        self.assertEqual(run("say 5 is 5"), "true\n")
        self.assertEqual(run("say 5 is 6"), "false\n")

    def test_is_equal_to(self):
        self.assertEqual(run("say 5 is equal to 5"), "true\n")

    def test_is_not_equal(self):
        self.assertEqual(run("say 5 is not equal to 6"), "true\n")
        self.assertEqual(run("say 5 is not equal to 5"), "false\n")

    def test_greater(self):
        self.assertEqual(run("say 10 is greater than 5"), "true\n")
        self.assertEqual(run("say 5 is greater than 10"), "false\n")

    def test_less(self):
        self.assertEqual(run("say 5 is less than 10"), "true\n")
        self.assertEqual(run("say 10 is less than 5"), "false\n")

    def test_greater_or_equal(self):
        self.assertEqual(run("say 5 is greater than or equal to 5"), "true\n")
        self.assertEqual(run("say 4 is greater than or equal to 5"), "false\n")

    def test_less_or_equal(self):
        self.assertEqual(run("say 5 is less than or equal to 5"), "true\n")
        self.assertEqual(run("say 6 is less than or equal to 5"), "false\n")


class TestSymbolComparisons(unittest.TestCase):
    def test_greater_than(self):
        self.assertEqual(run("say 10 > 5"), "true\n")
        self.assertEqual(run("say 5 > 10"), "false\n")

    def test_less_than(self):
        self.assertEqual(run("say 5 < 10"), "true\n")
        self.assertEqual(run("say 10 < 5"), "false\n")

    def test_greater_or_equal(self):
        self.assertEqual(run("say 5 >= 5"), "true\n")
        self.assertEqual(run("say 4 >= 5"), "false\n")

    def test_less_or_equal(self):
        self.assertEqual(run("say 5 <= 5"), "true\n")
        self.assertEqual(run("say 6 <= 5"), "false\n")

    def test_equal_single(self):
        self.assertEqual(run("say 5 = 5"), "true\n")
        self.assertEqual(run("say 5 = 6"), "false\n")

    def test_equal_double(self):
        self.assertEqual(run("say 5 == 5"), "true\n")
        self.assertEqual(run("say 5 == 6"), "false\n")

    def test_not_equal(self):
        self.assertEqual(run("say 5 != 6"), "true\n")
        self.assertEqual(run("say 5 != 5"), "false\n")

    def test_not_equal_strict(self):
        self.assertEqual(run("say 5 !== 6"), "true\n")
        self.assertEqual(run("say 5 !== 5"), "false\n")

    def test_string_equality(self):
        self.assertEqual(run('say "hello" == "hello"'), "true\n")
        self.assertEqual(run('say "hello" = "hello"'), "true\n")
        self.assertEqual(run('say "hello" != "world"'), "true\n")

    def test_in_if(self):
        src = '''
        let x be 10
        if x > 5 then
            say "big"
        end
        '''
        self.assertEqual(run(src), "big\n")

    def test_mixed_english_and_symbol(self):
        src = '''
        let x be 10
        if x is greater than 5 and x <= 15 then
            say "ok"
        end
        '''
        self.assertEqual(run(src), "ok\n")

    def test_chained_with_and(self):
        src = '''
        let x be 7
        if x >= 5 and x <= 10 then
            say "in range"
        end
        '''
        self.assertEqual(run(src), "in range\n")


class TestInterpreterLogic(unittest.TestCase):
    def test_and(self):
        self.assertEqual(run("say true and true"), "true\n")
        self.assertEqual(run("say true and false"), "false\n")

    def test_or(self):
        self.assertEqual(run("say false or true"), "true\n")
        self.assertEqual(run("say false or false"), "false\n")

    def test_not(self):
        self.assertEqual(run("say not true"), "false\n")
        self.assertEqual(run("say not false"), "true\n")

    def test_combined(self):
        # (true and not false) or false = true
        self.assertEqual(run("say true and not false or false"), "true\n")


class TestInterpreterVariables(unittest.TestCase):
    def test_reassign(self):
        src = '''
        let x be 5
        say x
        let x be 10
        say x
        '''
        self.assertEqual(run(src), "5\n10\n")

    def test_math_with_var(self):
        src = '''
        let a be 10
        let b be 3
        say a plus b
        say a times b
        '''
        self.assertEqual(run(src), "13\n30\n")

    def test_symbol_plus(self):
        src = 'say 3 + 4'
        self.assertEqual(run(src), "7\n")

    def test_symbol_minus(self):
        src = 'say 10 - 3'
        self.assertEqual(run(src), "7\n")

    def test_symbol_times(self):
        src = 'say 5 * 6'
        self.assertEqual(run(src), "30\n")

    def test_symbol_divide(self):
        src = 'say 20 / 4'
        self.assertEqual(run(src), "5\n")

    def test_symbol_mixed_with_keywords(self):
        src = 'say 2 + 3 times 4'
        self.assertEqual(run(src), "14\n")

    def test_symbol_complex_expr(self):
        src = 'say (10 - 2) * 3 + 1 / 1'
        self.assertEqual(run(src), "25\n")

    def test_undefined_variable(self):
        from src.errors import NameError_
        with self.assertRaises(NameError_):
            run("say x")


class TestInterpreterInput(unittest.TestCase):
    def test_ask(self):
        src = '''
        let name be ask "Name: "
        say "Hello, " , name
        '''
        self.assertEqual(run(src, stdin="Alice"), "Hello, Alice\n")

    def test_ask_number(self):
        src = '''
        let age be number(ask "Age: ")
        say age plus 1
        '''
        self.assertEqual(run(src, stdin="30"), "31\n")


class TestInterpreterLists(unittest.TestCase):
    def test_empty_list(self):
        self.assertEqual(run("say []"), "[]\n")

    def test_list_of_numbers(self):
        self.assertEqual(run("say [1, 2, 3]"), "[1, 2, 3]\n")

    def test_list_index(self):
        src = '''
        let nums be [10, 20, 30]
        say nums at 0
        say nums at 1
        say nums at 2
        '''
        self.assertEqual(run(src), "10\n20\n30\n")

    def test_size_of(self):
        src = '''
        let nums be [1, 2, 3, 4, 5]
        say size of nums
        '''
        self.assertEqual(run(src), "5\n")

    def test_with_added(self):
        src = '''
        let nums be [1, 2, 3]
        let more be nums with 4 added
        say more
        '''
        self.assertEqual(run(src), "[1, 2, 3, 4]\n")

    def test_list_size_of_text(self):
        self.assertEqual(run('say size of "hello"'), "5\n")

    def test_index_out_of_bounds(self):
        from src.errors import RuntimeError_
        with self.assertRaises(RuntimeError_):
            run("let nums be [1, 2]\nsay nums at 5")


class TestInterpreterIf(unittest.TestCase):
    def test_if_true(self):
        src = '''
        if true then
            say "yes"
        end
        '''
        self.assertEqual(run(src), "yes\n")

    def test_if_false(self):
        src = '''
        if false then
            say "yes"
        end
        '''
        self.assertEqual(run(src), "")

    def test_if_else(self):
        src = '''
        let x be 5
        if x is greater than 3 then
            say "big"
        else
            say "small"
        end
        '''
        self.assertEqual(run(src), "big\n")

    def test_if_else_2(self):
        src = '''
        let x be 1
        if x is greater than 3 then
            say "big"
        else
            say "small"
        end
        '''
        self.assertEqual(run(src), "small\n")

    def test_nested_if(self):
        src = '''
        let x be 10
        if x is greater than 5 then
            if x is greater than 8 then
                say "very big"
            else
                say "big"
            end
        end
        '''
        self.assertEqual(run(src), "very big\n")


class TestInterpreterLoops(unittest.TestCase):
    def test_repeat_5(self):
        src = '''
        repeat 3 times
            say "hi"
        end
        '''
        self.assertEqual(run(src), "hi\nhi\nhi\n")

    def test_repeat_zero(self):
        src = '''
        repeat 0 times
            say "hi"
        end
        '''
        self.assertEqual(run(src), "")

    def test_while(self):
        src = '''
        let i be 0
        while i is less than 3
            say i
            let i be i plus 1
        end
        '''
        self.assertEqual(run(src), "0\n1\n2\n")

    def test_for_each(self):
        src = '''
        let fruits be ["apple", "banana", "cherry"]
        for each fruit in fruits
            say fruit
        end
        '''
        self.assertEqual(run(src), "apple\nbanana\ncherry\n")

    def test_for_each_with_index(self):
        src = '''
        let nums be [10, 20, 30]
        for each n in nums
            say n times 2
        end
        '''
        self.assertEqual(run(src), "20\n40\n60\n")


class TestInterpreterFunctions(unittest.TestCase):
    def test_function_def_and_call(self):
        src = '''
        to greet name
            say "Hello, " , name
        end

        greet "Alice"
        greet "Bob"
        '''
        self.assertEqual(run(src), "Hello, Alice\nHello, Bob\n")

    def test_function_with_return(self):
        src = '''
        to square x
            return x times x
        end

        let result be square 5
        say result
        '''
        self.assertEqual(run(src), "25\n")

    def test_function_multiple_params(self):
        src = '''
        to add a b
            return a plus b
        end

        say add 3, 4
        '''
        self.assertEqual(run(src), "7\n")

    def test_function_wrong_arity(self):
        from src.errors import TypeError_
        src = '''
        to greet name
            say name
        end
        greet "Alice", "Bob"
        '''
        with self.assertRaises(TypeError_):
            run(src)

    def test_function_scope_isolation(self):
        src = '''
        let x be 10
        to f y
            let x be 99
            say x
        end
        f 0
        say x
        '''
        self.assertEqual(run(src), "99\n10\n")

    def test_recursion_factorial(self):
        src = '''
        to factorial n
            if n is less than 2 then
                return 1
            end
            return n times factorial(n minus 1)
        end

        say factorial 5
        '''
        self.assertEqual(run(src), "120\n")

    def test_recursion_fibonacci(self):
        src = '''
        to fib n
            if n is less than 2 then
                return n
            end
            return fib(n minus 1) plus fib(n minus 2)
        end

        say fib 10
        '''
        self.assertEqual(run(src), "55\n")


class TestInterpreterBuiltins(unittest.TestCase):
    def test_number(self):
        self.assertEqual(run('say number("42")'), "42\n")

    def test_text(self):
        self.assertEqual(run("say text(5)"), "5\n")

    def test_uppercase(self):
        self.assertEqual(run('say uppercase("hello")'), "HELLO\n")

    def test_lowercase(self):
        self.assertEqual(run('say lowercase("HELLO")'), "hello\n")

    def test_random_in_range(self):
        # Run a few times, each should be in [1, 10]
        for _ in range(5):
            result = run("let r be random 1, 10\nsay r")
            n = int(result.strip())
            self.assertGreaterEqual(n, 1)
            self.assertLessEqual(n, 10)


class TestInterpreterErrors(unittest.TestCase):
    def test_undefined_variable_message(self):
        from src.errors import NameError_
        try:
            run("say banana")
        except NameError_ as e:
            self.assertIn("banana", e.message)
            self.assertIn("let", e.message)

    def test_call_non_function(self):
        from src.errors import NameError_
        with self.assertRaises(NameError_):
            run("greet \"Alice\"")

    def test_type_error_message(self):
        from src.errors import TypeError_
        with self.assertRaises(TypeError_):
            run('say 5 plus "hello"')


class TestInterpreterPrograms(unittest.TestCase):
    def test_full_program(self):
        src = '''
        let name be ask "What is your name? "
        let age be number(ask "How old are you? ")

        say "Hello, " , name , "!"

        if age is greater than 30 then
            say "You are over 30"
        else
            say "You are 30 or younger"
        end
        '''
        out = run(src, stdin="Alice\n25")
        self.assertIn("Hello, Alice!", out)
        self.assertIn("You are 30 or younger", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
