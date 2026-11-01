"""Where things are: the checkout, and the folder through which configs reach its themes."""

from __future__ import annotations

from pathlib import Path

from nocturne import system

NAME = "dracula-nocturne"
PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PALETTE = ROOT / "palette.toml"
THEMES = ROOT / "themes"
APPS = PACKAGE / "apps"
DATA = PACKAGE / "data"


def link_dir() -> Path:
    """A link to themes/, so include lines stay short and survive moving the checkout:
    ~/.config/dracula-nocturne, or %APPDATA%\\dracula-nocturne on Windows."""
    return system.app_config() / NAME


def theme(rel: str) -> Path:
    """A theme file as the user's configs refer to it: through link_dir()."""
    return link_dir() / rel
