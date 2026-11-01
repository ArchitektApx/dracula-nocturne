"""Cursor: the VS Code extension, installed with Cursor's own command line."""

from __future__ import annotations

from nocturne import system
from nocturne.app import App, Group
from nocturne.extension import tiers

APP = App(
    id="cursor",
    title="Cursor",
    url="https://cursor.com",
    group=Group.EDITOR,
    binary="cursor",
    bundle="Cursor.app",
    platforms=system.EVERYWHERE,
    tiers=tiers("cursor", "Cursor.app"),
)
