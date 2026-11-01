"""The system nocturne runs on: which OS, and where the user's folders are."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from enum import StrEnum
from pathlib import Path


class OS(StrEnum):
    MACOS = "macos"
    LINUX = "linux"
    WINDOWS = "windows"


UNIX = frozenset({OS.MACOS, OS.LINUX})
EVERYWHERE = frozenset(OS)


def current() -> OS:
    if sys.platform == "darwin":
        return OS.MACOS
    if sys.platform == "win32":
        return OS.WINDOWS
    return OS.LINUX


def home() -> Path:
    return Path(os.environ.get("HOME") or Path.home())


def env_dir(var: str) -> Path | None:
    """A folder named by an environment variable; relative paths don't count (the XDG spec says so)."""
    value = os.environ.get(var)
    return Path(value) if value and Path(value).is_absolute() else None


def config_home() -> Path:
    """$XDG_CONFIG_HOME or ~/.config: where most of the themed apps look, on macOS too."""
    return env_dir("XDG_CONFIG_HOME") or home() / ".config"


def state_home() -> Path:
    if current() is OS.WINDOWS:
        return local_appdata()
    return env_dir("XDG_STATE_HOME") or home() / ".local" / "state"


def appdata() -> Path:
    return env_dir("APPDATA") or home() / "AppData" / "Roaming"


def local_appdata() -> Path:
    return env_dir("LOCALAPPDATA") or home() / "AppData" / "Local"


def app_support() -> Path:
    return home() / "Library" / "Application Support"


def app_config() -> Path:
    """Where tools that follow XDG on macOS and Linux keep their config on Windows: %APPDATA%."""
    return appdata() if current() is OS.WINDOWS else config_home()


def bundle(name: str) -> Path | None:
    """A macOS app bundle, in /Applications or ~/Applications."""
    if current() is not OS.MACOS:
        return None
    return next((p for p in (Path("/Applications", name), home() / "Applications" / name) if p.exists()), None)


def native_config() -> Path:
    """The OS's own config folder, which Rust's `dirs` and Go's os.UserConfigDir return:
    Application Support on macOS, %APPDATA% on Windows, the XDG folder on Linux."""
    return {OS.MACOS: app_support, OS.WINDOWS: appdata}.get(current(), config_home)()


def ask(argv: list[str]) -> str | None:
    """The first line a tool prints (`bat --config-dir`), or None if it isn't installed or fails."""
    if not shutil.which(argv[0]):
        return None
    try:
        done = subprocess.run(argv, capture_output=True, text=True, check=False, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    out = done.stdout.strip().splitlines()
    return out[0].strip() if done.returncode == 0 and out else None


def display(path: Path) -> str:
    """path with the home folder written as ~, for lines the user reads."""
    try:
        rel = path.relative_to(home())
    except ValueError:
        return str(path)
    return "~" if rel == Path() else f"~/{rel.as_posix()}"
