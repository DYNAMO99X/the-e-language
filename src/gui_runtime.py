"""GUI window runtime for the E language.

Follows the same pattern as turtle_runtime.py:
- WindowManager owns all GUI windows/widgets for one E program run.
- Text-mode fallback: every GUI command is logged to a list so tests
  can verify them without needing a display.
- Window mode: creates real tkinter widgets.

Usage from the interpreter:
    wm = GuiManager(requested_mode="auto")
    wm.create_window("win")
    wm.create_widget("button", "btn", "win", "Click Me")
    wm.set_property("win", "title", "My App")
    wm.place_widget("win", "btn", 0, 0)
    wm.handle_event("win", "on_click", "btn", "clicked")
    wm.show_window("win")
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any


class _Widget:
    """Internal representation of a GUI widget."""

    def __init__(self, widget_type: str, name: str, parent: str, text: str = ""):
        self.widget_type = widget_type
        self.name = name
        self.parent = parent
        self.text = text
        self.properties: Dict[str, Any] = {}
        self._tk_widget = None  # real tkinter widget in window mode

    def __repr__(self) -> str:
        return f"<{self.widget_type} '{self.name}' text='{self.text}'>"


class _Window:
    """Internal representation of a GUI window."""

    def __init__(self, name: str):
        self.name = name
        self.properties: Dict[str, Any] = {"title": "E Program", "width": 400, "height": 300}
        self.widgets: Dict[str, _Widget] = {}
        self._tk_root = None  # real tkinter root in window mode
        self._tk_frames: Dict[str, Any] = {}  # grid frame storage

    def __repr__(self) -> str:
        return f"<window '{self.name}' widgets={len(self.widgets)}>"


class GuiManager:
    """Manages GUI windows and widgets for an E program run.

    Follows the same dual-mode pattern as TurtleManager:
    - 'window' mode: creates real tkinter widgets
    - 'text' mode: logs commands for testing
    - 'auto' mode: tries window, falls back to text
    """

    def __init__(self, requested_mode: str = "auto"):
        self._mode = self._resolve_mode(requested_mode)
        self._windows: Dict[str, _Window] = {}
        self._widgets: Dict[str, _Widget] = {}  # flat lookup by name
        self._log: List[str] = []
        self._event_handlers: Dict[str, str] = {}  # "win.btn.clicked" -> handler_name
        self._tk_initialized = False

    # --- mode resolution ---

    def _resolve_mode(self, requested: str) -> str:
        if requested == "window":
            try:
                import tkinter
                return "window"
            except ImportError:
                return "text"
        if requested == "text":
            return "text"
        # auto: try window, fall back to text
        try:
            import tkinter
            return "window"
        except ImportError:
            return "text"

    @property
    def mode(self) -> str:
        return self._mode

    # --- window operations ---

    def create_window(self, name: str) -> str:
        """Create a new window. Returns the window name."""
        if name in self._windows:
            self._log.append(f"restart_window {name}")
            return name
        self._windows[name] = _Window(name)
        self._log.append(f"create_window {name}")

        if self._mode == "window" and not self._tk_initialized:
            try:
                import tkinter as tk
                self._tk_initialized = True
            except ImportError:
                pass

        return name

    def set_property(self, obj_name: str, prop: str, value: Any) -> None:
        """Set a property on a window or widget."""
        # Check windows first
        if obj_name in self._windows:
            win = self._windows[obj_name]
            win.properties[prop] = value
            self._log.append(f"set_property {obj_name} {prop} {value}")

            # Apply to real tkinter widget if in window mode
            if self._mode == "window" and win._tk_root:
                if prop == "title":
                    win._tk_root.title(str(value))
                elif prop == "width":
                    win._tk_root.geometry(f"{int(value)}x{win.properties.get('height', 300)}")
                elif prop == "height":
                    win._tk_root.geometry(f"{win.properties.get('width', 400)}x{int(value)}")
            return

        # Check widgets
        if obj_name in self._widgets:
            w = self._widgets[obj_name]
            w.properties[prop] = value
            # Update text in both modes
            if prop == "text":
                w.text = str(value)
            self._log.append(f"set_property {obj_name} {prop} {value}")

            # Apply to real tkinter widget if in window mode
            if self._mode == "window" and w._tk_widget:
                if prop == "text":
                    try:
                        w._tk_widget.config(text=str(value))
                    except Exception:
                        pass
                elif prop == "color":
                    try:
                        w._tk_widget.config(fg=str(value))
                    except Exception:
                        pass
                elif prop == "bg":
                    try:
                        w._tk_widget.config(bg=str(value))
                    except Exception:
                        pass
                elif prop == "font size":
                    try:
                        w._tk_widget.config(font=("", int(value)))
                    except Exception:
                        pass
            return

        raise ValueError(f"I don't know an object called '{obj_name}'")

    def get_property(self, obj_name: str, prop: str) -> Any:
        """Read a property from a window or widget."""
        if obj_name in self._windows:
            return self._windows[obj_name].properties.get(prop)
        if obj_name in self._widgets:
            w = self._widgets[obj_name]
            if prop == "text":
                return w.text
            return w.properties.get(prop)
        raise ValueError(f"I don't know an object called '{obj_name}'")

    # --- widget operations ---

    def create_widget(self, widget_type: str, name: str, parent: str, text: str = "") -> str:
        """Create a new widget on a window. Returns the widget name."""
        if parent not in self._windows:
            raise ValueError(
                f"I can't create a '{widget_type}' on '{parent}' — "
                f"'{parent}' is not a window."
            )
        self._widgets[name] = _Widget(widget_type, name, parent, text)
        self._log.append(f"create_widget {widget_type} {name} on {parent} text={text}")

        # Create real tkinter widget if in window mode
        if self._mode == "window" and parent in self._windows:
            win = self._windows[parent]
            if win._tk_root:
                try:
                    import tkinter as tk
                    if widget_type == "label":
                        w = tk.Label(win._tk_root, text=text)
                    elif widget_type == "button":
                        w = tk.Button(win._tk_root, text=text)
                    elif widget_type == "text input":
                        w = tk.Entry(win._tk_root)
                        w.insert(0, text)
                    else:
                        w = tk.Label(win._tk_root, text=text)
                    self._widgets[name]._tk_widget = w
                except Exception:
                    pass

        self._log.append(f"create_widget {widget_type} {name} on {parent} text='{text}'")
        return name

    def place_widget(self, window_name: str, widget_name: str, row: int, column: int) -> None:
        """Place a widget in a grid layout."""
        self._log.append(f"place_widget {widget_name} at row {row} column {column}")

        if self._mode == "window":
            win = self._windows.get(window_name)
            if win and win._tk_root:
                w = self._widgets.get(widget_name)
                if w and w._tk_widget:
                    try:
                        w._tk_widget.grid(row=row, column=column, padx=5, pady=5, sticky="ew")
                    except Exception:
                        pass

    def handle_event(self, window_name: str, handler_name: str, widget_name: str, event: str) -> None:
        """Bind an event handler to a widget."""
        key = f"{window_name}.{widget_name}.{event}"
        self._event_handlers[key] = handler_name
        self._log.append(f"handle_event {handler_name} when {widget_name} {event}")

    def show_window(self, window_name: str) -> None:
        """Show the window and start the event loop (window mode) or log it (text mode)."""
        self._log.append(f"show_window {window_name}")

        if self._mode == "window":
            win = self._windows.get(window_name)
            if win and win._tk_root:
                try:
                    win._tk_root.mainloop()
                except Exception:
                    pass

    def hide_window(self, window_name: str) -> None:
        """Hide the window."""
        self._log.append(f"hide_window {window_name}")

        if self._mode == "window":
            win = self._windows.get(window_name)
            if win and win._tk_root:
                try:
                    win._tk_root.withdraw()
                except Exception:
                    pass

    def get_text_of(self, widget_name: str) -> str:
        """Read the current text value of a widget."""
        if widget_name in self._widgets:
            w = self._widgets[widget_name]
            # In window mode, read from the real tkinter widget
            if self._mode == "window" and w._tk_widget:
                try:
                    return w._tk_widget.get()
                except Exception:
                    try:
                        return w._tk_widget.cget("text")
                    except Exception:
                        pass
            return w.text
        self._log.append(f"get_text_of {widget_name}")
        return ""

    # --- logging (for text mode tests) ---

    def get_log(self) -> List[str]:
        """Return the command log for text-mode testing."""
        return list(self._log)
