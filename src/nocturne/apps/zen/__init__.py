"""Zen Browser. theme: the accent colour and the mods' colours, in user.js. full: the halos in
userChrome.css, which build on the Arc 2.0 and Better Find Bar mods; those, Sine to install them,
Transparent Zen and two extensions are installed by hand, from where their makers publish them."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from nocturne import system
from nocturne.app import App, Group, Level, Tier
from nocturne.apps.zen import profile
from nocturne.steps import Link, Note

if TYPE_CHECKING:
    from nocturne.steps import Step


@dataclass(frozen=True)
class Requirement:
    id: str  # in Sine's mods.json, Zen's zen-themes.json or the profile's extensions.json
    name: str
    where: str
    optional: bool = False


REQUIREMENTS = [
    Requirement("sine", "Sine, the mod manager", "its installer: https://github.com/CosmoCreeper/Sine"),
    Requirement("Arc-2.0", "Arc 2.0", "Sine's marketplace (its README lists one more mod it needs)"),
    Requirement("ff-better-findbar", "Better Find Bar", "Sine's marketplace"),
    Requirement(
        "642854b5-88b4-4c40-b256-e035532109df",
        "Transparent Zen",
        "Sine: sameerasw/zen-themes, folder TransparentZen; or https://zen-browser.app/mods/642854b5-88b4-4c40-b256-e035532109df",
    ),
    Requirement(
        "{91aa3897-2634-4a8a-9092-279db23a7689}",
        "Zen Internet",
        "https://addons.mozilla.org/firefox/addon/zen-internet/",
    ),
    Requirement("addon@darkreader.org", "Dark Reader", "https://addons.mozilla.org/firefox/addon/darkreader/"),
    Requirement(
        "cb5efa80-f1e1-43ce-8c0b-fece8462d225",
        "Container Halo, so container tabs keep their colour",
        "https://zen-browser.app/mods/cb5efa80-f1e1-43ce-8c0b-fece8462d225",
        optional=True,
    ),
]

# What the window's see-through needs besides Transparent Zen
TRANSPARENCY = {
    system.OS.MACOS: "",
    system.OS.WINDOWS: "See-through needs Windows 11 22H2 or newer; Arc 2.0's README covers Windows 10.",
    system.OS.LINUX: (
        "See-through needs Transparent Zen's Linux option and a compositor that blurs"
        " (KDE does; its guide covers Hyprland)."
    ),
}


def requirements_note() -> Note:
    found = profile.find()
    have: set[str] = profile.installed(found) if found else set()
    lines = [f"{'✓' if r.id in have else '·' if r.optional else '✗'} {r.name}: {r.where}" for r in REQUIREMENTS]
    if extra := TRANSPARENCY[system.current()]:
        lines.append(extra)
    return Note("The halos build on these; install what's missing, then restart Zen:\n      " + "\n      ".join(lines))


def in_profile(rel: str, src: str) -> list[Step]:
    found = profile.find()
    if found is None:
        return [Note("Start Zen once, so it has a profile to install into.")] if rel == "user.js" else []
    return [Link(src, found / rel)]


APP = App(
    id="zen",
    title="Zen Browser",
    url="https://zen-browser.app",
    group=Group.DESKTOP,
    binary="zen",
    aliases=("zen-browser",),
    bundle="Zen.app",
    detect=lambda: profile.find() is not None,
    platforms=system.EVERYWHERE,
    tiers={
        Level.THEME: Tier(
            "the purple accent, and the colours of its mods", lambda: in_profile("user.js", "zen/user.js")
        ),
        Level.FULL: Tier(
            "halos on the selected tab, the URL bar and the find bar, with Arc 2.0 and see-through mods",
            lambda: [*in_profile("chrome/userChrome.css", "zen/userChrome.css"), requirements_note()],
        ),
    },
)
