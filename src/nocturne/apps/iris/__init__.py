"""iris: completion menus in the accents. Its theme.toml is the whole theme, so it's linked as is."""

from __future__ import annotations

from nocturne import system
from nocturne.app import App, Group, Level, Tier
from nocturne.steps import Link

APP = App(
    id="iris",
    title="iris",
    url="https://github.com/versenilvis/iris",
    group=Group.SHELL,
    binary="iris",
    tiers={
        Level.THEME: Tier(
            "completion menus", lambda: [Link("iris/theme.toml", system.config_home() / "iris" / "theme.toml")]
        ),
    },
)
