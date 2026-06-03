"""Tests for the GUI window runtime.

All tests run the interpreter in `text` mode so they don't need a display.
The runtime's command log and internal state are asserted against.
"""

from __future__ import annotations
import io
import sys
import unittest
from contextlib import redirect_stdout

from src.interpreter import Interpreter
from src.gui_runtime import GuiManager


def run(src: str, mode: str = "text") -> Interpreter:
    """Run E source and return the Interpreter (so tests can inspect state)."""
    interp = Interpreter("<gui-test>", turtle_mode=mode)
    buf = io.StringIO()
    with redirect_stdout(buf):
        interp.run_string(src)
    return interp


def get_gui(interp: Interpreter) -> GuiManager:
    return interp.gui


class TestGuiManagerBasic(unittest.TestCase):
    def test_initial_mode_is_text(self):
        gm = GuiManager(requested_mode="text")
        self.assertEqual(gm.mode, "text")

    def test_create_window(self):
        gm = GuiManager(requested_mode="text")
        gm.create_window("win")
        self.assertIn("win", gm._windows)

    def test_create_duplicate_window_logs_restart(self):
        gm = GuiManager(requested_mode="text")
        gm.create_window("win")
        gm.create_window("win")
        log = gm.get_log()
        self.assertEqual(log[0], "create_window win")
        self.assertEqual(log[1], "restart_window win")


class TestGuiWindowProperties(unittest.TestCase):
    def test_set_title(self):
        gm = GuiManager(requested_mode="text")
        gm.create_window("win")
        gm.set_property("win", "title", "My App")
        self.assertEqual(gm._windows["win"].properties["title"], "My App")
        self.assertIn("set_property win title My App", gm.get_log())

    def test_set_unknown_object_raises(self):
        gm = GuiManager(requested_mode="text")
        with self.assertRaises(ValueError):
            gm.set_property("nope", "title", "X")


class TestGuiWidgets(unittest.TestCase):
    def test_create_button(self):
        gm = GuiManager(requested_mode="text")
        gm.create_window("win")
        gm.create_widget("button", "btn", "win", "Click Me")
        self.assertIn("btn", gm._widgets)
        self.assertEqual(gm._widgets["btn"].text, "Click Me")
        self.assertEqual(gm._widgets["btn"].parent, "win")

    def test_create_label(self):
        gm = GuiManager(requested_mode="text")
        gm.create_window("win")
        gm.create_widget("label", "lbl", "win", "Hello")
        self.assertEqual(gm._widgets["lbl"].text, "Hello")

    def test_create_widget_on_non_window_raises(self):
        gm = GuiManager(requested_mode="text")
        with self.assertRaises(ValueError):
            gm.create_widget("button", "btn", "nope", "X")

    def test_place_widget(self):
        gm = GuiManager(requested_mode="text")
        gm.create_window("win")
        gm.create_widget("button", "btn", "win", "OK")
        gm.place_widget("win", "btn", 0, 1)
        log = gm.get_log()
        self.assertIn("place_widget btn at row 0 column 1", log)

    def test_handle_event(self):
        gm = GuiManager(requested_mode="text")
        gm.create_window("win")
        gm.create_widget("button", "btn", "win", "OK")
        gm.handle_event("win", "on_click", "btn", "clicked")
        self.assertEqual(gm._event_handlers["win.btn.clicked"], "on_click")

    def test_show_window(self):
        gm = GuiManager(requested_mode="text")
        gm.create_window("win")
        gm.show_window("win")
        self.assertIn("show_window win", gm.get_log())

    def test_hide_window(self):
        gm = GuiManager(requested_mode="text")
        gm.create_window("win")
        gm.hide_window("win")
        self.assertIn("hide_window win", gm.get_log())

    def test_get_text_of(self):
        gm = GuiManager(requested_mode="text")
        gm.create_window("win")
        gm.create_widget("text input", "name", "win", "Alice")
        self.assertEqual(gm.get_text_of("name"), "Alice")

    def test_set_widget_text(self):
        gm = GuiManager(requested_mode="text")
        gm.create_window("win")
        gm.create_widget("label", "lbl", "win", "old")
        gm.set_property("lbl", "text", "new")
        self.assertEqual(gm._widgets["lbl"].text, "new")


class TestGuiInterpreterIntegration(unittest.TestCase):
    """Run E source code that uses GUI constructs in text mode."""

    def test_create_window_with_let(self):
        interp = run('let win be window')
        gui = get_gui(interp)
        self.assertIn("win", gui._windows)

    def test_create_button_with_let(self):
        interp = run('let win be window\nlet btn be button "Click Me" on win')
        gui = get_gui(interp)
        self.assertIn("btn", gui._widgets)
        self.assertEqual(gui._widgets["btn"].text, "Click Me")

    def test_create_label_with_let(self):
        interp = run('let win be window\nlet lbl be label "Hello" on win')
        gui = get_gui(interp)
        self.assertIn("lbl", gui._widgets)
        self.assertEqual(gui._widgets["lbl"].text, "Hello")

    def test_set_window_title(self):
        interp = run('let win be window\nset win title to "My App"')
        gui = get_gui(interp)
        self.assertEqual(gui._windows["win"].properties["title"], "My App")

    def test_set_label_text(self):
        interp = run('let win be window\nlet lbl be label "old" on win\nset lbl text to "new"')
        gui = get_gui(interp)
        self.assertEqual(gui._widgets["lbl"].text, "new")

    def test_set_button_font_size(self):
        interp = run('let win be window\nlet btn be button "OK" on win\nset btn font size to 16')
        gui = get_gui(interp)
        self.assertEqual(gui._widgets["btn"].properties.get("font size"), 16)

    def test_set_button_color(self):
        interp = run('let win be window\nlet btn be button "OK" on win\nset btn color to "blue"')
        gui = get_gui(interp)
        self.assertEqual(gui._widgets["btn"].properties.get("color"), "blue")

    def test_place_widget(self):
        interp = run(
            'let win be window\n'
            'let btn be button "OK" on win\n'
            'make win place btn at row 0 and column 1'
        )
        gui = get_gui(interp)
        log = gui.get_log()
        self.assertIn("place_widget btn at row 0 column 1", log)

    def test_handle_event(self):
        interp = run(
            'let win be window\n'
            'let btn be button "OK" on win\n'
            'make win do on_click when btn clicked'
        )
        gui = get_gui(interp)
        self.assertEqual(gui._event_handlers["win.btn.clicked"], "on_click")

    def test_show_window(self):
        interp = run('let win be window\nshow win')
        gui = get_gui(interp)
        self.assertIn("show_window win", gui.get_log())

    def test_hide_window(self):
        interp = run('let win be window\nhide win')
        gui = get_gui(interp)
        self.assertIn("hide_window win", gui.get_log())

    def test_text_of_reads_widget(self):
        interp = run(
            'let win be window\n'
            'let name be text input "Alice" on win\n'
            'say text of name'
        )
        self.assertIn("Alice", interp.output_buffer)

    def test_full_gui_program(self):
        """A complete GUI program: create window, widgets, set properties, show."""
        src = (
            'let win be window\n'
            'set win title to "My App"\n'
            'let greet be label "Hello" on win\n'
            'let btn be button "Click Me" on win\n'
            'set greet font size to 14\n'
            'set btn color to "green"\n'
            'make win place greet at row 0 and column 0\n'
            'make win place btn at row 1 and column 0\n'
            'show win'
        )
        interp = run(src)
        gui = get_gui(interp)
        self.assertIn("win", gui._windows)
        self.assertIn("greet", gui._widgets)
        self.assertIn("btn", gui._widgets)
        self.assertEqual(gui._windows["win"].properties["title"], "My App")
        self.assertEqual(gui._widgets["greet"].properties.get("font size"), 14)
        self.assertEqual(gui._widgets["btn"].properties.get("color"), "green")

    def test_nothing_widget_raises(self):
        with self.assertRaises(Exception):
            run('let win be window\nlet btn be button "OK" on nothing')

    def test_unknown_widget_object_raises(self):
        with self.assertRaises(Exception):
            run('let win be window\nset nope text to "X"')


if __name__ == "__main__":
    unittest.main()
