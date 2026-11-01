"""JankyBorders: a purple-to-pink gradient around the focused window (macOS)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from nocturne import system
from nocturne.app import App, Group, Level, Tier
from nocturne.steps import Link, Note

if TYPE_CHECKING:
    from pathlib import Path

RESTART = "Restart borders to load it: brew services restart borders"


def bordersrc() -> Path:
    # borders reads ~/.config/borders/bordersrc and ~/.bordersrc only, whatever XDG_CONFIG_HOME says
    return system.home() / ".config" / "borders" / "bordersrc"


APP = App(
    id="borders",
    title="JankyBorders",
    url="https://github.com/FelixKratz/JankyBorders",
    group=Group.DESKTOP,
    binary="borders",
    platforms=frozenset({system.OS.MACOS}),
    tiers={
        Level.THEME: Tier(
            "a purple-to-pink gradient around the focused window",
            lambda: [
                Link("borders/bordersrc", bordersrc()),
                Note(RESTART),
            ],
        ),
    },
)
