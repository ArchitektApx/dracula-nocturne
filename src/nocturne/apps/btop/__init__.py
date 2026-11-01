"""btop: boxes in the accents, meters as gradients from a dim to a bright version of one colour."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from nocturne import paths, system
from nocturne.app import App, Group, Level, Tier
from nocturne.steps import Link, Note
from nocturne.template import header

if TYPE_CHECKING:
    from nocturne.palette import Color, Palette
    from nocturne.steps import Step

THEME = "btop/dracula-nocturne.theme"


def generate(p: Palette) -> dict[str, str]:
    def ramp(name: str, base: Color, top: Color) -> list[tuple[str, str]]:
        # start: the colour half-faded into the background, so idle meters stay quiet
        return [(f"{name}_start", base.mix(p["bg"], 0.5).hex), (f"{name}_mid", base.hex), (f"{name}_end", top.hex)]

    keys: list[tuple[str, str]] = [
        ("main_bg", p["bg"].hex),
        ("main_fg", p["fg"].hex),
        ("title", p["fg"].hex),
        ("hi_fg", p["pink"].hex),  # the shortcut letters in box titles
        ("selected_bg", p["selection"].hex),
        ("selected_fg", p["fg"].hex),
        ("inactive_fg", p["line"].hex),
        ("graph_text", p["comment"].hex),
        ("meter_bg", p["surface"].hex),
        ("proc_misc", p["pink"].hex),
        ("cpu_box", p["purple"].hex),
        ("mem_box", p["purple"].hex),
        ("net_box", p["purple"].hex),
        ("proc_box", p["purple"].hex),
        ("div_line", p["surface"].hex),
        *ramp("temp", p["purple"], p["red"]),
        ("cpu_start", p["cyan"].hex),
        ("cpu_mid", p["purple"].hex),
        ("cpu_end", p["pink"].hex),
        *ramp("free", p["green"], p["bright.green"]),
        *ramp("cached", p["cyan"], p["bright.cyan"]),
        *ramp("available", p["orange"], p["yellow"]),
        *ramp("used", p["pink"], p["bright.pink"]),
        *ramp("download", p["purple"], p["bright.purple"]),
        *ramp("upload", p["pink"], p["bright.pink"]),
        ("process_start", p["cyan"].hex),
        ("process_mid", p["purple"].hex),
        ("process_end", p["pink"].hex),
    ]
    head = header(p, "btop") + '# In btop\'s themes folder, with color_theme = "dracula-nocturne" in btop.conf.\n\n'
    return {"dracula-nocturne.theme": head + "".join(f'theme[{k}]="{v}"\n' for k, v in keys)}


SELECT = Note('Select it: Esc > Options > Color theme, or color_theme = "dracula-nocturne" in btop.conf')


def steps() -> list[Step]:
    """~/.config/btop/themes; on Windows, btop4win keeps its themes next to its exe, which may not be
    writable (Program Files), and then it's a copy by hand. btop writes btop.conf back on exit, so a
    line added there wouldn't last: selecting the theme is a note."""
    themes = system.config_home() / "btop" / "themes"
    if system.current() is system.OS.WINDOWS and (exe := shutil.which("btop4win")):
        themes = Path(exe).resolve().parent / "themes"
        if not os.access(themes.parent, os.W_OK):
            return [Note(f"Copy {system.display(paths.theme(THEME))} into {themes}"), SELECT]
    return [Link(THEME, themes / "dracula-nocturne.theme"), SELECT]


APP = App(
    id="btop",
    title="btop",
    url="https://github.com/aristocratos/btop",
    group=Group.TOOL,
    binary="btop",
    aliases=("btop4win",),
    platforms=system.EVERYWHERE,
    generate=generate,
    tiers={
        Level.THEME: Tier("meters as gradients, boxes in the accents", steps),
    },
)
