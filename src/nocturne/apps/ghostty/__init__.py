"""Ghostty. The colours and look it shares with kitty are in nocturne/terminal.py.

theme: the colours, as a Ghostty theme. look: see-through and blurred, a blinking block cursor
with a trail (templates/shaders), no macOS title bar, padding. full: the Nerd Font.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from nocturne import paths, system
from nocturne.app import App, Group, Level, Tier
from nocturne.steps import Line, Link
from nocturne.template import header
from nocturne.terminal import BLUR, FONT, OPACITY, PADDING, terminal_colors

if TYPE_CHECKING:
    from pathlib import Path

    from nocturne.palette import Palette
    from nocturne.steps import Step


def generate(p: Palette) -> dict[str, str]:
    c = terminal_colors(p)
    theme = [
        f"background = {c['background']}",
        f"foreground = {c['foreground']}",
        f"cursor-color = {c['cursor']}",
        f"cursor-text = {c['cursor_text']}",
        f"selection-background = {c['selection']}",
        "selection-foreground = cell-foreground",  # selected text keeps its colours, as in kitty
        f"split-divider-color = {c['divider']}",
        "",
        *(f"palette = {i}={color.hex}" for i, color in enumerate(p.ansi)),
    ]
    look = [
        f"background-opacity = {OPACITY}",
        f"background-blur = {BLUR}",  # macOS, and KDE on Linux
        "unfocused-split-opacity = 0.85",
        "cursor-style = block",
        "cursor-style-blink = true",
        "custom-shader = shaders/cursor_trail.glsl",  # relative to this file
        "macos-titlebar-style = hidden",
        f"window-padding-x = {PADDING[0]}",
        f"window-padding-y = {PADDING[1]}",
        "window-padding-balance = true",
    ]
    return {
        "dracula-nocturne": header(p, "Ghostty") + "\n" + "\n".join(theme) + "\n",
        "look.ghostty": header(p, "Ghostty, the look") + "\n" + "\n".join(look) + "\n",
        "full.ghostty": header(p, "Ghostty, the font") + f'\nfont-family = "{FONT}"\n',
    }


def configs() -> list[Path]:
    """Ghostty's config files in the order it reads them; on macOS, Application Support comes last."""
    folders = [system.config_home() / "ghostty"]
    if system.current() is system.OS.MACOS:
        folders.append(system.app_support() / "com.mitchellh.ghostty")
    return [folder / name for folder in folders for name in ("config", "config.ghostty")]


def config() -> Path:
    """The config file Ghostty reads last, so its lines win; config.ghostty if there's none yet."""
    found = [f for f in configs() if f.exists()]
    return found[-1] if found else system.config_home() / "ghostty" / "config.ghostty"


def include(name: str) -> Step:
    # included files are read after the file that names them, so their settings win
    return Line(config(), f"config-file = ?{system.display(paths.theme(f'ghostty/{name}'))}", also=tuple(configs()))


APP = App(
    id="ghostty",
    title="Ghostty",
    url="https://ghostty.org",
    group=Group.TERMINAL,
    binary="ghostty",
    bundle="Ghostty.app",
    generate=generate,
    tiers={
        Level.THEME: Tier(
            "the terminal colours",
            lambda: [
                # user themes are read from the XDG folder only, on macOS too
                Link("ghostty/dracula-nocturne", system.config_home() / "ghostty" / "themes" / "dracula-nocturne"),
                Line(config(), "theme = dracula-nocturne", also=tuple(configs())),
            ],
        ),
        Level.LOOK: Tier(
            "see-through with blur, a blinking cursor with a trail, no macOS title bar, padding",
            lambda: [include("look.ghostty")],
        ),
        Level.FULL: Tier(f"the {FONT} font", lambda: [include("full.ghostty")]),
    },
)
