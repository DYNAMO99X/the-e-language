"""Turtle runtime for the E language.

Provides a `Turtle` class that wraps Python's built-in `turtle` module,
plus a `TurtleManager` that tracks multiple named turtles within a single
E program.

Supports two modes:

* `window` — opens a real tkinter window and draws visually.
* `text`   — headless. No window is opened; instead, every command is
             appended to a per-turtle command log. Useful for tests and
             for running on a machine with no display (e.g. CI).

The mode is selected at construction time. When `auto` is requested, the
runtime tries to open a window; if tkinter fails for any reason, it
falls back to text mode silently.
"""

from __future__ import annotations
import math
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------- one turtle ----------

class Turtle:
    """A single named turtle. Maintains its own state.

    In window mode, every state-changing method also forwards to Python's
    `turtle.Turtle` so a window appears. In text mode, state is tracked
    locally and commands are appended to `self.log`.
    """

    def __init__(self, name: str, mode: str):
        self.name = name
        self.mode = mode                # 'window' | 'text'
        self.log: List[str] = []

        # State
        self.x: float = 0.0
        self.y: float = 0.0
        self.heading: float = 0.0       # degrees; 0 = right (east)
        self.pen_down: bool = True
        self.pen_color: str = "black"
        self.pen_size: int = 1
        self.background: str = "white"
        self.visible: bool = True
        self.speed: int = 3             # 0 = fastest, 1-10 = slow to medium

        # Underlying Python turtle (only in window mode)
        self._t: Optional[object] = None
        if self.mode == "window":
            try:
                import turtle as _py_turtle
                self._t = _py_turtle.Turtle()
                self._t.speed(self.speed)
            except Exception:
                # tkinter failed — fall back to text mode for this turtle
                self.mode = "text"
                self._t = None

    # ----- low-level helpers -----

    def _log(self, msg: str) -> None:
        if self.mode == "text":
            self.log.append(f">> {msg}")

    def _to_radians(self) -> float:
        return math.radians(self.heading)

    # ----- movement -----

    def forward(self, n: float) -> None:
        if self.pen_down and self._t is not None:
            self._t.forward(n)         # type: ignore[union-attr]
        rad = self._to_radians()
        self.x += n * math.cos(rad)
        self.y += n * math.sin(rad)
        self._log(f"forward {n}")

    def backward(self, n: float) -> None:
        if self.pen_down and self._t is not None:
            self._t.backward(n)        # type: ignore[union-attr]
        rad = self._to_radians()
        self.x -= n * math.cos(rad)
        self.y -= n * math.sin(rad)
        self._log(f"backward {n}")

    def left(self, n: float) -> None:
        if self._t is not None:
            self._t.left(n)             # type: ignore[union-attr]
        self.heading = (self.heading + n) % 360
        self._log(f"left {n}")

    def right(self, n: float) -> None:
        if self._t is not None:
            self._t.right(n)            # type: ignore[union-attr]
        self.heading = (self.heading - n) % 360
        self._log(f"right {n}")

    # ----- cursor visibility -----

    def hide(self) -> None:
        self.visible = False
        if self._t is not None:
            self._t.hideturtle()        # type: ignore[union-attr]
        self._log("hide")

    def show(self) -> None:
        self.visible = True
        if self._t is not None:
            self._t.showturtle()        # type: ignore[union-attr]
        self._log("show")

    # ----- pen state -----
    # Methods are named raise_pen/lower_pen so they don't collide with the
    # self.pen_down boolean attribute.

    def raise_pen(self) -> None:
        self.pen_down = False
        if self._t is not None:
            self._t.penup()             # type: ignore[union-attr]
        self._log("pen_up")

    def lower_pen(self) -> None:
        self.pen_down = True
        if self._t is not None:
            self._t.pendown()           # type: ignore[union-attr]
        self._log("pen_down")

    # ----- clearing / resetting -----

    def clear(self) -> None:
        if self._t is not None:
            self._t.clear()             # type: ignore[union-attr]
        self.log.clear()
        self._log("erase_all")

    def home(self) -> None:
        if self._t is not None:
            self._t.home()              # type: ignore[union-attr]
        self.x = 0.0
        self.y = 0.0
        self.heading = 0.0
        self._log("home")

    def reset(self) -> None:
        """Factory reset: clear + home + restore all defaults."""
        if self._t is not None:
            self._t.reset()             # type: ignore[union-attr]
        self.x = 0.0
        self.y = 0.0
        self.heading = 0.0
        self.pen_down = True
        self.pen_color = "black"
        self.pen_size = 1
        self.background = "white"
        self.visible = True
        self.speed = 3
        self.log.clear()
        self._log("restart")

    # ----- shape drawing -----

    def circle(self, r: float) -> None:
        if self._t is not None:
            self._t.circle(r)           # type: ignore[union-attr]
        # Approximate: 36 sample points (full circle) and update position
        # based on the heading. Python's turtle.circle() with the default
        # extent=360 leaves the turtle at the start; we mirror that.
        self._log(f"draw_circle {r}")

    def dot(self, size: float) -> None:
        if self._t is not None:
            self._t.dot(int(size))      # type: ignore[union-attr]
        self._log(f"draw_dot {size}")

    # ----- positioning -----

    def goto_relative(self, x_amount: float, x_dir: str,
                      y_amount: float, y_dir: str) -> None:
        dx = x_amount if x_dir == "right" else -x_amount
        dy = y_amount if y_dir == "up"    else -y_amount
        target_x = self.x + dx
        target_y = self.y + dy
        if self._t is not None:
            self._t.goto(target_x, target_y)  # type: ignore[union-attr]
        self.x = target_x
        self.y = target_y
        self._log(f"goto {x_amount} {x_dir} and {y_amount} {y_dir}")

    def goto_absolute(self, x: float, y: float) -> None:
        if self._t is not None:
            self._t.goto(x, y)          # type: ignore[union-attr]
        self.x = x
        self.y = y
        self._log(f"go_to {x} and {y}")

    # ----- speed -----

    def set_speed(self, n: int) -> None:
        self.speed = max(0, min(10, int(n)))
        if self._t is not None:
            self._t.speed(self.speed)   # type: ignore[union-attr]
        self._log(f"speed {self.speed}")

    # ----- properties (for `set`) -----

    def set_pen_color(self, color: str) -> None:
        self.pen_color = str(color)
        if self._t is not None:
            self._t.pencolor(self.pen_color)  # type: ignore[union-attr]
        self._log(f"pen_color {self.pen_color}")

    def set_pen_size(self, n: int) -> None:
        self.pen_size = max(1, int(n))
        if self._t is not None:
            self._t.pensize(self.pen_size)     # type: ignore[union-attr]
        self._log(f"pen_size {self.pen_size}")

    def set_background(self, color: str) -> None:
        self.background = str(color)
        if self._t is not None:
            try:
                import turtle as _py_turtle
                _py_turtle.bgcolor(self.background)  # type: ignore[union-attr]
            except Exception:
                pass
        self._log(f"background {self.background}")

    # ----- finalization -----

    def close(self) -> None:
        """Release the underlying turtle (if any). Safe to call multiple times."""
        if self._t is not None:
            try:
                self._t.hideturtle()    # type: ignore[union-attr]
            except Exception:
                pass


# ---------- the manager ----------

class TurtleManager:
    """Owns all turtles for one E program run.

    Mode can be 'auto' (try to open a window, fall back to text), 'window'
    (force a window), or 'text' (headless, no window).
    """

    def __init__(self, requested_mode: str = "auto"):
        if requested_mode not in ("auto", "window", "text"):
            raise ValueError(
                f"turtle mode must be 'auto', 'window', or 'text', "
                f"got {requested_mode!r}"
            )
        self.requested_mode = requested_mode
        self.turtles: Dict[str, Turtle] = {}
        self._resolved_mode: Optional[str] = None
        self._init_error: Optional[str] = None

    def _resolve_mode(self) -> str:
        if self._resolved_mode is not None:
            return self._resolved_mode
        if self.requested_mode == "text":
            self._resolved_mode = "text"
            return self._resolved_mode
        # Try window mode
        try:
            import tkinter                      # noqa: F401
            self._resolved_mode = "window"
        except Exception as e:
            self._init_error = str(e)
            self._resolved_mode = "text"
        return self._resolved_mode

    def create(self, name: str) -> Turtle:
        if name in self.turtles:
            raise RuntimeError(
                f"You already made a turtle called '{name}'. "
                f"Give it a different name."
            )
        mode = self._resolve_mode()
        t = Turtle(name, mode)
        self.turtles[name] = t
        return t

    def get(self, name: str) -> Turtle:
        if name not in self.turtles:
            raise RuntimeError(
                f"I don't know a turtle called '{name}'. "
                f"Did you forget to write `let {name} be turtle` first?"
            )
        return self.turtles[name]

    def close_all(self) -> None:
        for t in self.turtles.values():
            t.close()
        # If we opened any window, try to clean it up. Importing inside
        # the function keeps the import optional.
        if self._resolved_mode == "window":
            try:
                import turtle as _py_turtle
                _py_turtle.bye()
            except Exception:
                # We're probably not in the main thread; just let the
                # window be. Python's atexit will clean up.
                pass
