"""AeroSpace: no colours of its own, but the gaps and the JankyBorders start that complete the desktop."""

from __future__ import annotations

from nocturne import paths, system
from nocturne.app import App, Group, Level, Tier
from nocturne.steps import Note


def note() -> Note:
    snippet = (paths.THEMES / "aerospace" / "aerospace.toml").read_text(encoding="utf-8")
    body = "\n".join(f"      {line}" for line in snippet.splitlines() if line and not line.startswith("#"))
    source = system.display(paths.theme("aerospace/aerospace.toml"))
    return Note(f"aerospace.toml has no includes, so add this to yours (from {source}):\n{body}")


APP = App(
    id="aerospace",
    title="AeroSpace",
    url="https://github.com/nikitabobko/AeroSpace",
    group=Group.DESKTOP,
    binary="aerospace",
    bundle="AeroSpace.app",
    platforms=frozenset({system.OS.MACOS}),
    tiers={Level.LOOK: Tier("gaps around the windows, and JankyBorders started with it", lambda: [note()])},
)
