"""Tests for the turtle drawing builtin.

All tests run the interpreter in `text` mode so they don't need a display
or a tkinter window. The runtime's command log and internal state are
asserted against.
"""

from __future__ import annotations
import io
import math
import sys
import unittest
from contextlib import redirect_stdout

from src.interpreter import Interpreter


def run(src: str, mode: str = "text") -> Interpreter:
    """Run E source and return the Interpreter (so tests can inspect state)."""
    interp = Interpreter("<turtle-test>", turtle_mode=mode)
    buf = io.StringIO()
    with redirect_stdout(buf):
        interp.run_string(src)
    return interp


def get_ada(interp: Interpreter):
    return interp.turtles.get("ada")


class TestTurtleCreation(unittest.TestCase):
    def test_create_with_let(self):
        interp = run("let ada be turtle")
        self.assertIn("ada", interp.turtles.turtles)

    def test_create_appears_in_text_mode_log_on_first_action(self):
        # The 'turtle' literal itself does not log; first action does.
        interp = run("let ada be turtle\nmove ada forward 10")
        t = get_ada(interp)
        self.assertEqual(t.log, [">> forward 10"])

    def test_duplicate_create_raises(self):
        with self.assertRaises(Exception) as cm:
            run("let ada be turtle\nlet ada be turtle")
        self.assertIn("ada", str(cm.exception))

    def test_undefined_turtle_raises(self):
        with self.assertRaises(Exception) as cm:
            run("move ada forward 10")
        self.assertIn("ada", str(cm.exception))


class TestTurtleMove(unittest.TestCase):
    def test_forward_moves_x(self):
        interp = run("let ada be turtle\nmove ada forward 50")
        t = get_ada(interp)
        self.assertEqual(t.x, 50.0)
        self.assertEqual(t.y, 0.0)

    def test_right_then_forward_moves_down(self):
        # Right 90 means facing down (heading = -90 in our coord system,
        # or equivalently 270 mod 360).
        interp = run("let ada be turtle\nmove ada right 90\nmove ada forward 30")
        t = get_ada(interp)
        self.assertEqual(t.heading, 270.0)
        self.assertAlmostEqual(t.x, 0.0)
        self.assertAlmostEqual(t.y, -30.0)

    def test_left_then_forward_moves_up(self):
        interp = run("let ada be turtle\nmove ada left 90\nmove ada forward 20")
        t = get_ada(interp)
        self.assertEqual(t.heading, 90.0)
        self.assertAlmostEqual(t.x, 0.0)
        self.assertAlmostEqual(t.y, 20.0)

    def test_backward(self):
        interp = run("let ada be turtle\nmove ada backward 25")
        t = get_ada(interp)
        self.assertEqual(t.x, -25.0)

    def test_square(self):
        src = """
        let ada be turtle
        move ada forward 10
        move ada right 90
        move ada forward 10
        move ada right 90
        move ada forward 10
        move ada right 90
        move ada forward 10
        move ada right 90
        """
        interp = run(src)
        t = get_ada(interp)
        # Back to start (0, 0), facing the original direction
        self.assertAlmostEqual(t.x, 0.0)
        self.assertAlmostEqual(t.y, 0.0)
        self.assertEqual(t.heading, 0.0)


class TestTurtleMake(unittest.TestCase):
    def test_hide_and_show(self):
        interp = run("let ada be turtle\nmake ada hide\nmake ada show")
        t = get_ada(interp)
        self.assertTrue(t.visible)
        # Log shows both events (show did NOT clear log; only erase_all / restart do)
        self.assertIn(">> hide", t.log)
        self.assertIn(">> show", t.log)

    def test_close_and_open_pen(self):
        interp = run("let ada be turtle\nmake ada close pen\nmake ada open pen")
        t = get_ada(interp)
        self.assertTrue(t.pen_down)
        self.assertIn(">> pen_up", t.log)
        self.assertIn(">> pen_down", t.log)

    def test_erase_all_clears_log(self):
        interp = run("let ada be turtle\nmove ada forward 5\nmake ada erase all")
        t = get_ada(interp)
        # After erase_all, the log should only contain "erase_all"
        self.assertEqual(t.log, [">> erase_all"])

    def test_restart_resets_everything(self):
        src = """
        let ada be turtle
        move ada forward 50
        move ada right 45
        set ada pen color to "red"
        set ada pen size to 5
        make ada restart
        """
        interp = run(src)
        t = get_ada(interp)
        self.assertEqual(t.x, 0.0)
        self.assertEqual(t.y, 0.0)
        self.assertEqual(t.heading, 0.0)
        self.assertEqual(t.pen_color, "black")
        self.assertEqual(t.pen_size, 1)
        # Log is cleared by restart
        self.assertEqual(t.log, [">> restart"])

    def test_go_home(self):
        interp = run("let ada be turtle\nmove ada forward 50\nmove ada right 90\nmake ada go home")
        t = get_ada(interp)
        self.assertEqual(t.x, 0.0)
        self.assertEqual(t.y, 0.0)
        self.assertEqual(t.heading, 0.0)

    def test_draw_circle(self):
        interp = run("let ada be turtle\nmake ada draw circle 30")
        t = get_ada(interp)
        self.assertIn(">> draw_circle 30", t.log)

    def test_draw_dot(self):
        interp = run("let ada be turtle\nmake ada draw dot 5")
        t = get_ada(interp)
        self.assertIn(">> draw_dot 5", t.log)

    def test_speed(self):
        interp = run("let ada be turtle\nmake ada speed 7")
        t = get_ada(interp)
        self.assertEqual(t.speed, 7)

    def test_speed_clamps_to_range(self):
        interp = run("let ada be turtle\nmake ada speed 99")
        t = get_ada(interp)
        self.assertEqual(t.speed, 10)


class TestTurtleGoto(unittest.TestCase):
    def test_goto_relative_right_and_up(self):
        interp = run("let ada be turtle\nmake ada goto 50 right and 20 up")
        t = get_ada(interp)
        self.assertEqual(t.x, 50.0)
        self.assertEqual(t.y, 20.0)

    def test_goto_relative_left_and_down(self):
        interp = run("let ada be turtle\nmake ada goto 100 left and 70 down")
        t = get_ada(interp)
        self.assertEqual(t.x, -100.0)
        self.assertEqual(t.y, -70.0)

    def test_goto_relative_is_additive(self):
        # Goto adds to the current position, doesn't replace it.
        interp = run("let ada be turtle\nmove ada forward 10\nmake ada goto 5 right and 0 up")
        t = get_ada(interp)
        self.assertEqual(t.x, 15.0)

    def test_goto_absolute(self):
        interp = run("let ada be turtle\nmove ada forward 10\nmake ada go to 50 and 20")
        t = get_ada(interp)
        # Absolute: replaces current position
        self.assertEqual(t.x, 50.0)
        self.assertEqual(t.y, 20.0)


class TestTurtleSet(unittest.TestCase):
    def test_set_pen_color(self):
        interp = run('let ada be turtle\nset ada pen color to "red"')
        t = get_ada(interp)
        self.assertEqual(t.pen_color, "red")

    def test_set_pen_size(self):
        interp = run("let ada be turtle\nset ada pen size to 5")
        t = get_ada(interp)
        self.assertEqual(t.pen_size, 5)

    def test_set_background(self):
        interp = run('let ada be turtle\nset ada background to "white"')
        t = get_ada(interp)
        self.assertEqual(t.background, "white")


class TestTurtleProperties(unittest.TestCase):
    def test_heading_query(self):
        interp = run("let ada be turtle\nmove ada right 45")
        # The `ada heading` becomes a CallExpression at parse time and
        # dispatches to a turtle property read at runtime.
        out = io.StringIO()
        with redirect_stdout(out):
            interp.run_string('say ada heading')
        # heading is 315 (or -45), so output should be 315.0
        self.assertIn("315", out.getvalue())

    def test_x_and_y_queries(self):
        src = """
        let ada be turtle
        move ada forward 50
        move ada right 90
        move ada forward 20
        say ada x
        say ada y
        """
        out = io.StringIO()
        with redirect_stdout(out):
            Interpreter("<test>", turtle_mode="text").run_string(src)
        # x ≈ 50, y ≈ -20 (allow for floating point fuzz)
        text = out.getvalue()
        # Check that "50" appears (as "50" or "50.0" or "49.999...")
        self.assertTrue(
            "50" in text or "49.99" in text,
            f"Expected '50' in output, got: {text!r}",
        )
        self.assertIn("-20", text)


class TestTurtleMultipleTurtles(unittest.TestCase):
    def test_two_turtles_independent(self):
        src = """
        let ada be turtle
        let bob be turtle
        move ada forward 100
        move bob right 90
        move bob forward 50
        """
        interp = run(src)
        ada = interp.turtles.get("ada")
        bob = interp.turtles.get("bob")
        self.assertEqual(ada.x, 100.0)
        self.assertEqual(ada.heading, 0.0)
        self.assertAlmostEqual(bob.x, 0.0)
        self.assertAlmostEqual(bob.y, -50.0)
        self.assertEqual(bob.heading, 270.0)


class TestTurtleIntegration(unittest.TestCase):
    def test_full_program_works(self):
        # Smoke test of every kind of statement working together.
        src = """
        let ada be turtle
        make ada speed 3
        set ada pen color to "blue"
        move ada forward 50
        move ada right 90
        move ada forward 50
        make ada draw circle 20
        make ada go to 0 and 0
        say "done"
        """
        out = io.StringIO()
        with redirect_stdout(out):
            Interpreter("<test>", turtle_mode="text").run_string(src)
        self.assertIn("done", out.getvalue())

    def test_turtle_in_function(self):
        src = """
        to draw_square side
            let ada be turtle
            move ada forward side
            move ada right 90
            move ada forward side
            move ada right 90
            move ada forward side
            move ada right 90
            move ada forward side
            move ada right 90
        end
        draw_square 50
        """
        interp = Interpreter("<test>", turtle_mode="text")
        buf = io.StringIO()
        with redirect_stdout(buf):
            interp.run_string(src)
        # Drawing a 50x50 square should return to (0, 0) facing 0.
        t = interp.turtles.get("ada")
        self.assertAlmostEqual(t.x, 0.0)
        self.assertAlmostEqual(t.y, 0.0)
        self.assertEqual(t.heading, 0.0)


if __name__ == "__main__":
    unittest.main()
