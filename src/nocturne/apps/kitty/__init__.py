"""kitty: Ghostty's colours and look, plus tabs and split borders. Its cursor trail is built in."""

from __future__ import annotations

from typing import TYPE_CHECKING

from nocturne import paths, system
from nocturne.app import App, Group, Level, Tier
from nocturne.steps import Line
from nocturne.template import header
from nocturne.terminal import BLUR, FONT, OPACITY, PADDING, terminal_colors

if TYPE_CHECKING:
    from pathlib import Path

    from nocturne.palette import Palette
    from nocturne.steps import Step


def generate(p: Palette) -> dict[str, str]:
    c = terminal_colors(p)
    theme = [
        f"background {c['background']}",
        f"foreground {c['foreground']}",
        f"cursor {c['cursor']}",
        f"cursor_text_color {c['cursor_text']}",
        f"selection_background {c['selection']}",
        "selection_foreground none",
        f"url_color {p['cyan'].hex}",
        "",
        *(f"color{i} {color.hex}" for i, color in enumerate(p.ansi)),
        "",
        "# Splits: the divider as in Ghostty, plus a purple border on the active window",
        f"active_border_color {p['purple'].hex}",
        f"inactive_border_color {c['divider']}",
        f"bell_border_color {p['red'].hex}",
        "",
        "# Tabs: pink for the current one, surface for the rest",
        f"tab_bar_background {p['bg'].hex}",
        f"active_tab_background {p['pink'].hex}",
        f"active_tab_foreground {p['bg'].hex}",
        f"inactive_tab_background {p['surface'].hex}",
        f"inactive_tab_foreground {p['comment'].hex}",
        "",
        "# Marks (kitty's highlight markers)",
        *(
            f"mark{i}_{part}"
            for i, color in enumerate(("purple", "pink", "yellow"), 1)
            for part in (f"background {p[color].hex}", f"foreground {p['bg'].hex}")
        ),
    ]
    look = [
        f"background_opacity {OPACITY}",
        f"background_blur {BLUR}",  # macOS, and Wayland compositors with the blur extension
        "inactive_text_alpha 0.85",
        "cursor_shape block",
        "cursor_stop_blinking_after 0",
        "cursor_trail 1",
        "cursor_trail_decay 0.1 0.4",
        f"window_padding_width {PADDING[1]} {PADDING[0]}",
        "tab_bar_style powerline",
        "# per system: KITTY_OS is macos, linux or bsd",
        "globinclude look-${KITTY_OS}.conf",
    ]
    return {
        "dracula-nocturne.conf": header(p, "kitty") + "\n" + "\n".join(theme) + "\n",
        "look.conf": header(p, "kitty, the look") + "\n" + "\n".join(look) + "\n",
        "look-macos.conf": header(p, "kitty on macOS, the look") + "\nhide_window_decorations titlebar-only\n",
        "full.conf": header(p, "kitty, the font") + f'\nfont_family family="{FONT}"\n',
    }


def conf() -> Path:
    return (system.env_dir("KITTY_CONFIG_DIRECTORY") or system.config_home() / "kitty") / "kitty.conf"


def include(name: str) -> Step:
    return Line(conf(), f"include {system.display(paths.theme(f'kitty/{name}'))}")


APP = App(
    id="kitty",
    title="kitty",
    url="https://sw.kovidgoyal.net/kitty",
    group=Group.TERMINAL,
    binary="kitty",
    bundle="kitty.app",
    generate=generate,
    tiers={
        Level.THEME: Tier("Ghostty's colours, plus tabs and split borders", lambda: [include("dracula-nocturne.conf")]),
        Level.LOOK: Tier(
            "see-through with blur, a blinking cursor with a trail, powerline tabs, no macOS title bar",
            lambda: [include("look.conf")],
        ),
        Level.FULL: Tier(f"the {FONT} font", lambda: [include("full.conf")]),
    },
)
