"""lazygit: borders, selection and commit markers. LG_CONFIG_FILE layers the theme over the user's config."""

from __future__ import annotations

from pathlib import Path

from nocturne import paths, shells, system
from nocturne.app import App, Group, Level, Tier
from nocturne.steps import Touch


def config_dir() -> Path:
    """What lazygit reports, else its documented default: CONFIG_DIR, then XDG_CONFIG_HOME,
    then the OS's folder (Application Support on macOS, %LOCALAPPDATA% on Windows)."""
    if found := system.ask(["lazygit", "--print-config-dir"]):
        return Path(found)
    if found := system.env_dir("CONFIG_DIR"):
        return found
    if system.env_dir("XDG_CONFIG_HOME") or system.current() is system.OS.LINUX:
        return system.config_home() / "lazygit"
    return (system.local_appdata() if system.current() is system.OS.WINDOWS else system.app_support()) / "lazygit"


def config_files() -> str:
    """The user's config, then the theme: lazygit merges them in that order."""
    return f"{shells.var(config_dir() / 'config.yml')},{shells.var(paths.theme('lazygit/dracula-nocturne.yml'))}"


APP = App(
    id="lazygit",
    title="lazygit",
    url="https://github.com/jesseduffield/lazygit",
    group=Group.TOOL,
    binary="lazygit",
    platforms=system.EVERYWHERE,
    tiers={
        Level.THEME: Tier(
            "borders, selection and commit markers",
            # lazygit won't start while a file in LG_CONFIG_FILE is missing, and makes its own only without it
            lambda: [Touch(config_dir() / "config.yml"), *shells.exported("LG_CONFIG_FILE", config_files())],
        ),
    },
)
