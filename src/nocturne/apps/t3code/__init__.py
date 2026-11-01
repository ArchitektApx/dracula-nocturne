"""T3 Code: a theme file in T3's export format, every role from the palette's [ui].

T3 Code publishes the themes in <T3CODE_HOME or ~/.t3>/userdata/themes/, and the file name is
the theme's id. It won't read a link there, so the theme is a copy that install refreshes.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from nocturne import system
from nocturne.app import App, Group, Level, Tier
from nocturne.steps import Copy, Note

if TYPE_CHECKING:
    from pathlib import Path

    from nocturne.palette import Palette


def generate(p: Palette) -> dict[str, str]:
    theme = {
        "version": 1,
        "name": p.name,
        "appearance": "dark",
        "colors": {role: color.hex for role, color in p.section("ui").items()},
    }
    return {"dracula-nocturne.json": json.dumps(theme, indent=2) + "\n"}


def themes_dir() -> Path:
    return (system.env_dir("T3CODE_HOME") or system.home() / ".t3") / "userdata" / "themes"


APP = App(
    id="t3code",
    title="T3 Code",
    url="https://github.com/pingdotgg/t3code",
    group=Group.EDITOR,
    binary="t3",
    detect=lambda: themes_dir().parent.is_dir(),  # noqa: PLW0108  # its binary is rarely on PATH, its data is
    platforms=system.EVERYWHERE,
    generate=generate,
    tiers={
        Level.THEME: Tier(
            "every role of T3's theme editor",
            lambda: [
                Copy("t3code/dracula-nocturne.json", themes_dir() / "dracula-nocturne.json"),
                Note(
                    "Select it in Settings > Appearance, or for every connected client: t3 theme set dracula-nocturne"
                ),
            ],
        ),
    },
)
