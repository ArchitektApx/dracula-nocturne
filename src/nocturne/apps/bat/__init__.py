"""bat: Pierre Dark's code colours as a TextMate theme (nocturne/textmate.py), selected in its config."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from nocturne import system
from nocturne.app import App, Group, Level, Tier
from nocturne.steps import Line, Link, Run
from nocturne.textmate import tmtheme

if TYPE_CHECKING:
    from nocturne.palette import Palette


THEME = "Dracula Nocturne"


def generate(p: Palette) -> dict[str, str]:
    return {f"{THEME}.tmTheme": tmtheme(p)}


def binary() -> str:
    """bat, or batcat as Debian and Ubuntu call it."""
    return "batcat" if not shutil.which("bat") and shutil.which("batcat") else "bat"


def config_dir() -> Path:
    if found := system.ask([binary(), "--config-dir"]):
        return Path(found)
    return system.env_dir("BAT_CONFIG_DIR") or system.app_config() / "bat"


def config_file() -> Path:
    found = system.ask([binary(), "--config-file"])
    return Path(found) if found else system.env_dir("BAT_CONFIG_PATH") or config_dir() / "config"


APP = App(
    id="bat",
    title="bat",
    url="https://github.com/sharkdp/bat",
    group=Group.TOOL,
    binary="bat",
    aliases=("batcat",),
    platforms=system.EVERYWHERE,
    generate=generate,
    tiers={
        Level.THEME: Tier(
            "Pierre Dark's code colours, the same as in VS Code",
            lambda: [
                Link(f"bat/{THEME}.tmTheme", config_dir() / "themes" / f"{THEME}.tmTheme"),
                Run((binary(), "cache", "--build"), "bat only sees new themes after rebuilding its cache"),
                Line(config_file(), f'--theme="{THEME}"'),
            ],
        ),
    },
)
