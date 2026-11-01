"""Zen's profile in use, and which mods and extensions it has."""

from __future__ import annotations

import configparser
import json
from pathlib import Path
from typing import cast

from nocturne import system


def roots() -> list[Path]:
    """Where Zen keeps profiles.ini. Linux moved to XDG in Zen 1.18.6b, keeping ~/.zen if it's there."""
    home = system.home()
    match system.current():
        case system.OS.MACOS:
            return [system.app_support() / "zen"]
        case system.OS.WINDOWS:
            return [system.appdata() / "zen"]
        case _:
            flatpak = home / ".var" / "app" / "app.zen_browser.zen"
            return [home / ".zen", system.config_home() / "zen", flatpak / ".zen", flatpak / "config" / "zen"]


def _resolve(root: Path, section: configparser.SectionProxy, key: str) -> Path | None:
    value = section.get(key)
    if not value:
        return None
    path = Path(value) if section.get("IsRelative", "1") == "0" else root / value
    return path if path.is_dir() else None


def find() -> Path | None:
    """The default profile: the install's default from installs.ini, else Default=1 in profiles.ini."""
    for root in roots():
        for ini, key in (("installs.ini", "Default"), ("profiles.ini", "Path")):
            parser = configparser.ConfigParser(interpolation=None, strict=False)
            try:
                parser.read(root / ini, encoding="utf-8")
            except (configparser.Error, UnicodeDecodeError):
                continue
            for section in map(parser.__getitem__, parser.sections()):
                if ini == "profiles.ini" and section.get("Default") != "1":
                    continue
                if found := _resolve(root, section, key):
                    return found
    return None


def _ids(file: Path, pick: str | None = None) -> set[str]:
    """The keys of a JSON object, or the "id"s of a list under `pick`; empty if it can't be read."""
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    if pick is None:
        return set(cast("dict[str, object]", data)) if isinstance(data, dict) else set()
    items = cast("dict[str, list[dict[str, object]]]", data).get(pick, []) if isinstance(data, dict) else []
    return {str(item.get("id")) for item in items}


def installed(profile: Path) -> set[str]:
    """Ids of what's in the profile: Sine itself ("sine"), mods from Sine or Zen's store, extensions."""
    chrome = profile / "chrome"
    found = _ids(chrome / "sine-mods" / "mods.json") | _ids(profile / "zen-themes.json")
    found |= _ids(profile / "extensions.json", pick="addons")
    if (chrome / "JS" / "sine.sys.mjs").exists():
        found.add("sine")
    return found
