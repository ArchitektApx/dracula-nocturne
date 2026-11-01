"""yazi: a flavor, with code previews in the bat theme's colours."""

from __future__ import annotations

from typing import TYPE_CHECKING

from nocturne import paths, system
from nocturne.app import App, Group, Level, Tier
from nocturne.steps import Copy, Link, Note
from nocturne.textmate import tmtheme

if TYPE_CHECKING:
    from pathlib import Path

    from nocturne.palette import Palette
    from nocturne.steps import Step

FLAVOR = "dracula-nocturne.yazi"


def generate(p: Palette) -> dict[str, str]:
    return {f"{FLAVOR}/tmtheme.xml": tmtheme(p), "theme.toml": '[flavor]\ndark = "dracula-nocturne"\n'}


def config_dir() -> Path:
    """YAZI_CONFIG_HOME, else ~/.config/yazi, or %APPDATA%\\yazi\\config on Windows."""
    if found := system.env_dir("YAZI_CONFIG_HOME"):
        return found
    if system.current() is system.OS.WINDOWS:
        return system.appdata() / "yazi" / "config"
    return system.config_home() / "yazi"


def steps() -> list[Step]:
    """The flavor, and a theme.toml that selects it, unless the user has a theme.toml of their own."""
    theme = config_dir() / "theme.toml"
    own = theme.exists() and theme.read_bytes() != (paths.THEMES / "yazi" / "theme.toml").read_bytes()
    if own:
        return [
            flavor(),
            Note(f'Select it in {system.display(theme)}:\n      [flavor]\n      dark = "dracula-nocturne"'),
        ]
    return everything()


def flavor() -> Step:
    return Link(f"yazi/{FLAVOR}", config_dir() / "flavors" / FLAVOR)


def everything() -> list[Step]:
    # theme.toml as a copy: it's the user's file to add to
    return [flavor(), Copy("yazi/theme.toml", config_dir() / "theme.toml")]


APP = App(
    id="yazi",
    title="yazi",
    url="https://yazi-rs.github.io",
    group=Group.TOOL,
    binary="yazi",
    platforms=system.EVERYWHERE,
    generate=generate,
    tiers={Level.THEME: Tier("a flavor, with code previews in the bat colours", steps, cleanup=everything)},
)
