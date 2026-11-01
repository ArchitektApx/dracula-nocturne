"""LS_COLORS (GNU ls, fd, tree, completion menus) and LSCOLORS (the BSD ls of macOS), from eza's table."""

from __future__ import annotations

from typing import TYPE_CHECKING

from nocturne import shells
from nocturne.app import App, Group, Level, Tier
from nocturne.filekinds import LSCOLORS, ls_colors
from nocturne.template import header

if TYPE_CHECKING:
    from nocturne.palette import Palette

NOTE = (
    "# The eza theme's file colours, for GNU ls, fd, tree, zsh completion and the like.\n"
    "# LSCOLORS does the same for the BSD ls of macOS (with CLICOLOR=1 or ls -G).\n"
)


def generate(p: Palette) -> dict[str, str]:
    value = ls_colors(p)
    return {
        "ls_colors.sh": header(p, "LS_COLORS (bash, zsh)")
        + NOTE
        + f"export LS_COLORS='{value}'\nexport LSCOLORS='{LSCOLORS}'\n",
        "ls_colors.fish": header(p, "LS_COLORS (fish)")
        + NOTE
        + f"set -gx LS_COLORS '{value}'\nset -gx LSCOLORS '{LSCOLORS}'\n",
    }


APP = App(
    id="ls_colors",
    title="LS_COLORS",
    url="https://www.gnu.org/software/coreutils/manual/html_node/dircolors-invocation.html",
    group=Group.SHELL,
    generate=generate,
    tiers={
        Level.THEME: Tier(
            "eza's file colours for ls, fd, tree and completion menus", lambda: shells.sourced("ls_colors/ls_colors")
        )
    },
)
