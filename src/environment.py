"""Scoped environment (variable + function storage) for the interpreter.

Implemented in Phase 5.
"""

from __future__ import annotations
from typing import Any, Optional, Callable, List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.ast_nodes import FunctionDef


class Environment:
    def __init__(self, parent: Optional["Environment"] = None):
        self.parent = parent
        self.variables: dict = {}
        self.functions: dict = {}

    def define(self, name: str, value: Any) -> None:
        self.variables[name] = value

    def get(self, name: str) -> Any:
        env = self
        while env is not None:
            if name in env.variables:
                return env.variables[name]
            env = env.parent
        raise KeyError(name)

    def set(self, name: str, value: Any) -> None:
        env = self
        while env is not None:
            if name in env.variables:
                env.variables[name] = value
                return
            env = env.parent
        raise KeyError(name)

    def has(self, name: str) -> bool:
        env = self
        while env is not None:
            if name in env.variables:
                return True
            env = env.parent
        return False

    def define_function(self, name: str, func: "FunctionDef") -> None:
        self.functions[name] = func

    def get_function(self, name: str) -> Optional["FunctionDef"]:
        env = self
        while env is not None:
            if name in env.functions:
                return env.functions[name]
            env = env.parent
        return None

    def child(self) -> "Environment":
        return Environment(parent=self)
