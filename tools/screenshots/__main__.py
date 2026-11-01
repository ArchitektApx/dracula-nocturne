"""Screenshots for the README: assets/apps/<app>-<level>.png, and assets/hero.svg.

    uv run tools/screenshots [app ...]           default: every app
    uv run tools/screenshots --placeholders      only make the missing placeholders
    uv run tools/screenshots social              only assets/social-preview.png

Needs tmux, the apps themselves, and Chrome or Chromium for the PNGs. Apps that aren't installed
are skipped and keep their old picture.
"""

import shutil
import subprocess
import sys
from collections.abc import Callable

from ansi import AnsiHtml
from capture import Home, capture, home, scratch
from frames import placeholder, png, render
from hero import hero
from scenes import SCENES, Scene
from social import social

from nocturne import paths
from nocturne.app import Level
from nocturne.apps import registry
from nocturne.palette import load

OUT = paths.ROOT / "assets" / "apps"


def shoot(scene: Scene, conv: AnsiHtml, home_at: Callable[[Level], Home], only_placeholders: bool) -> None:
    dest = OUT / f"{scene.name}.png"
    if scene.command is None:  # a real screenshot, taken by hand; until there is one, a placeholder
        if not dest.exists():
            png(placeholder(conv.palette, registry()[scene.app].title, str(scene.level)), (760, 316), dest)
            print(f"placeholder {scene.name}")
        return
    if only_placeholders:
        return
    needs = scene.needs or registry()[scene.app].binary
    if needs and not shutil.which(needs) and scene.app not in {"ghostty", "kitty"}:
        print(f"skipped {scene.name}: {needs} isn't installed")
        return
    h = home_at(scene.level)
    try:
        pane = capture(h, scene.command(h), scene.size, scene.keys, scene.wait)
    finally:
        if scene.after:
            subprocess.run(scene.after, capture_output=True, check=False)
    render(conv, pane, scene.frame, scene.size, dest)
    print(f"captured {scene.name}")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    only_placeholders = "--placeholders" in sys.argv
    palette = load(paths.PALETTE)
    conv = AnsiHtml(palette)
    OUT.mkdir(parents=True, exist_ok=True)
    (paths.ROOT / "assets" / "hero.svg").write_text(hero(palette), encoding="utf-8")
    desktop = paths.ROOT / "assets" / "desktop.png"
    if not desktop.exists():  # the whole desktop is a real screenshot; until there is one, a placeholder
        png(placeholder(palette, "The whole desktop", "every level"), (1200, 520), desktop)
    base = scratch()
    homes: dict[Level, Home] = {}

    def home_at(level: Level) -> Home:  # each level's home is made once, when a scene first needs it
        if level not in homes:
            homes[level] = home(base, level)
        return homes[level]

    try:
        for scene in SCENES:
            if not args or scene.app in args:
                shoot(scene, conv, home_at, only_placeholders)
        if (not args or "social" in args) and not only_placeholders:
            social(conv, home_at, paths.ROOT / "assets" / "social-preview.png")
            print("captured social-preview")
    finally:
        shutil.rmtree(base, ignore_errors=True)


main()
