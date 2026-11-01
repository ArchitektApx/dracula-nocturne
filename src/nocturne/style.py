"""nocturne's own output: colours (off with NO_COLOR or when not on a terminal) and one-line reports."""

from __future__ import annotations

import os
import sys


def _on() -> bool:
    return sys.stdout.isatty() and "NO_COLOR" not in os.environ and os.environ.get("TERM") != "dumb"


def _fg(hex_: str) -> str:
    r, g, b = int(hex_[1:3], 16), int(hex_[3:5], 16), int(hex_[5:7], 16)
    return f"\033[38;2;{r};{g};{b}m" if _on() else ""


RESET = "\033[0m" if _on() else ""
PINK = _fg("#ff79c6")
PURPLE = _fg("#bd93f9")
GREEN = _fg("#50fa7b")
YELLOW = _fg("#f1fa8c")
RED = _fg("#ff5555")
DIM = _fg("#6272a4")


def say(sign: str, color: str, text: str) -> None:
    """One indented report line: + added, - removed, ~ moved, = already there, ! problem, → by hand."""
    print(f"  {color}{sign}{RESET} {text}")


def heading(text: str) -> None:
    print(f"{PINK}{text}{RESET}")
