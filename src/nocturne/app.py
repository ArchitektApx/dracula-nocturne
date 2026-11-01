"""A themed app: how to spot it, the theme files it gets, and the steps of each level.

Levels build on each other. `theme` is the colours only; `look` adds the settings that make up the
rest of the look (transparency, the cursor trail); `full` goes as far as a whole setup (LazyVim, a
complete p10k config). An app only has the levels that make sense for it; most start at theme.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from enum import IntEnum
from typing import TYPE_CHECKING

from nocturne import system

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from nocturne.palette import Palette
    from nocturne.steps import Step


class Level(IntEnum):
    THEME = 1
    LOOK = 2
    FULL = 3

    def __str__(self) -> str:
        return self.name.lower()


class Group(IntEnum):
    """Where an app shows up in `nocturne list`."""

    TERMINAL = 1
    SHELL = 2
    EDITOR = 3
    TOOL = 4
    DESKTOP = 5


@dataclass(frozen=True)
class Tier:
    about: str
    steps: Callable[[], list[Step]]
    # every step install may have taken, for undo, when `steps` depends on what it finds
    # (an existing LazyVim config gets one file, an empty folder the whole starter)
    cleanup: Callable[[], list[Step]] | None = None

    def undo_steps(self) -> list[Step]:
        return (self.cleanup or self.steps)()


@dataclass(frozen=True)
class App:
    id: str  # also the name of its package in nocturne/apps and its folder in themes/
    title: str
    url: str
    group: Group
    tiers: Mapping[Level, Tier]
    platforms: frozenset[system.OS] = system.UNIX
    # how to spot it: a binary on PATH (or one of its aliases), a macOS app bundle, or a check of its own
    binary: str | None = None
    aliases: tuple[str, ...] = ()
    bundle: str | None = None
    detect: Callable[[], bool] | None = None
    # theme files written by code, {name: content} in themes/<id>/, next to the rendered templates
    generate: Callable[[Palette], dict[str, str]] | None = field(default=None, repr=False)

    def supported(self) -> bool:
        return system.current() in self.platforms

    def found(self) -> str | None:
        """The binary's name on PATH, if it's there."""
        return next((name for name in (self.binary, *self.aliases) if name and shutil.which(name)), None)

    def present(self) -> bool:
        if self.found() or (self.detect and self.detect()):
            return True
        if self.bundle and system.bundle(self.bundle):
            return True
        return self.binary is None and self.detect is None

    def level(self, wanted: Level) -> Level | None:
        """The highest level this app has, up to wanted; None if it only starts above (AeroSpace)."""
        return max((level for level in self.tiers if level <= wanted), default=None)

    def steps(self, upto: Level = Level.FULL) -> list[Step]:
        """What install does: the steps of every level up to upto."""
        return [step for level in sorted(self.tiers) if level <= upto for step in self.tiers[level].steps()]

    def undo_steps(self, above: Level | None = None) -> list[Step]:
        """What undo takes back out: everything, or only the levels above `above`."""
        low = above or 0
        return [step for level in sorted(self.tiers) if level > low for step in self.tiers[level].undo_steps()]
