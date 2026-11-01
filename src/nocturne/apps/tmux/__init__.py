"""tmux 3.3+: pill tabs, a prefix badge, pane borders and popups."""

from __future__ import annotations

from typing import TYPE_CHECKING

from nocturne import paths, system
from nocturne.app import App, Group, Level, Tier
from nocturne.steps import Line

if TYPE_CHECKING:
    from pathlib import Path


def confs() -> tuple[Path, Path]:
    """tmux reads both, ~/.tmux.conf first: the line goes into the one the user has."""
    return system.config_home() / "tmux" / "tmux.conf", system.home() / ".tmux.conf"


def conf() -> Path:
    xdg, classic = confs()
    return classic if classic.exists() and not xdg.exists() else xdg


APP = App(
    id="tmux",
    title="tmux",
    url="https://github.com/tmux/tmux",
    group=Group.TERMINAL,
    binary="tmux",
    tiers={
        Level.THEME: Tier(
            "pill tabs, a prefix badge, pane borders, popups",
            lambda: [
                Line(
                    conf(), f"source-file -q {system.display(paths.theme('tmux/dracula-nocturne.conf'))}", also=confs()
                )
            ],
        ),
    },
)
