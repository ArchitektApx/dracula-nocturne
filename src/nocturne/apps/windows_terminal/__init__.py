"""Windows Terminal: JSON fragments (learn.microsoft.com/windows/terminal/json-fragment-extensions).

A fragment adds the colour scheme and updates the profiles Windows Terminal makes itself; what the
user's settings.json says about a profile still wins.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from nocturne import system
from nocturne.app import App, Group, Level, Tier
from nocturne.steps import Link
from nocturne.terminal import FONT, OPACITY, PADDING, terminal_colors

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from nocturne.palette import Palette

SCHEME = "Dracula Nocturne"
ANSI = ["black", "red", "green", "yellow", "blue", "purple", "cyan", "white"]
# The profiles a fragment may update (fixed GUIDs): Command Prompt, Windows PowerShell, PowerShell 7
# and Git Bash
PROFILES = [
    "{0caa0dad-35be-5f56-a8ff-afceeeaa6101}",
    "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",
    "{574e775e-4f2a-5b96-ac1e-a2962a402336}",
    "{2ece5bfe-50ed-5f3a-ab87-5cd4baafed2b}",
]


def fragment(settings: Mapping[str, object], schemes: list[dict[str, str]] | None = None) -> str:
    data: dict[str, object] = {"profiles": [{"updates": guid, **settings} for guid in PROFILES]}
    if schemes:
        data["schemes"] = schemes
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def generate(p: Palette) -> dict[str, str]:
    c = terminal_colors(p)
    names = ANSI + [f"bright{n.title()}" for n in ANSI]
    scheme = {
        "name": SCHEME,
        "background": c["background"],
        "foreground": c["foreground"],
        "cursorColor": c["cursor"],
        "selectionBackground": c["selection"],
        **{name: color.hex for name, color in zip(names, p.ansi, strict=True)},
    }
    look = {
        "opacity": round(OPACITY * 100),
        "useAcrylic": True,  # the blur
        "cursorShape": "filledBox",
        "padding": f"{PADDING[0]}, {PADDING[1]}",
    }
    return {
        "dracula-nocturne.json": fragment({"colorScheme": SCHEME}, [scheme]),
        "look.json": fragment(look),
        "full.json": fragment({"font": {"face": FONT}}),
    }


def fragments() -> Path:
    return system.local_appdata() / "Microsoft" / "Windows Terminal" / "Fragments" / "dracula-nocturne"


def link(name: str) -> Link:
    return Link(f"windows_terminal/{name}", fragments() / name)


APP = App(
    id="windows_terminal",
    title="Windows Terminal",
    url="https://github.com/microsoft/terminal",
    group=Group.TERMINAL,
    binary="wt",
    platforms=frozenset({system.OS.WINDOWS}),
    generate=generate,
    tiers={
        Level.THEME: Tier(
            "the colour scheme, on the PowerShell, Command Prompt and Git Bash profiles",
            lambda: [link("dracula-nocturne.json")],
        ),
        Level.LOOK: Tier("see-through acrylic, a block cursor, padding", lambda: [link("look.json")]),
        Level.FULL: Tier(f"the {FONT} font", lambda: [link("full.json")]),
    },
)
