"""Powerlevel10k: p10k has no themes, only parameters in the user's config, so the theme is an
overlay sourced after ~/.p10k.zsh. At full, ~/.p10k.zsh itself: the lean config the look was made
with, as a copy that's yours to change."""

from __future__ import annotations

from typing import TYPE_CHECKING

from nocturne import paths, shells, system
from nocturne.app import App, Group, Level, Tier
from nocturne.steps import Copy, Line

if TYPE_CHECKING:
    from pathlib import Path


def config() -> Path:
    """Where `p10k configure` writes its config."""
    return shells.zshrc().parent / ".p10k.zsh"


def used() -> bool:
    """A p10k config is there, or .zshrc loads powerlevel10k: plain zsh users don't get the overlay."""
    if config().exists() or (system.home() / ".p10k.zsh").exists():
        return True
    try:
        rc = shells.zshrc().read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return "p10k" in rc or "powerlevel10k" in rc


def overlay() -> Line:
    # at the end of .zshrc, so it comes after the user's `source ~/.p10k.zsh`
    f = shells.var(paths.theme("p10k/dracula-nocturne.zsh"))
    return Line(shells.zshrc(), f'[ -r "{f}" ] && . "{f}"', only_existing=True)


APP = App(
    id="p10k",
    title="Powerlevel10k",
    url="https://github.com/romkatv/powerlevel10k",
    group=Group.SHELL,
    detect=used,
    tiers={
        Level.THEME: Tier("colours and rounded tiles over your own p10k config", lambda: [overlay()]),
        Level.FULL: Tier("the whole prompt: two lines, lean, transient", lambda: [Copy("p10k/p10k.zsh", config())]),
    },
)
