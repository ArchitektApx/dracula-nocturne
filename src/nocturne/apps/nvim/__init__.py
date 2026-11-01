"""Neovim: a colorscheme with Pierre Dark's code colours, linked into the config folder so it needs no
plugin manager. At full, LazyVim with it: the starter config, or just the colorscheme spec for
an existing LazyVim config."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from nocturne import paths, system
from nocturne.app import App, Group, Level, Tier
from nocturne.steps import Copy, Link, Note

if TYPE_CHECKING:
    from pathlib import Path

    from nocturne.steps import Step

THEME_FILES = ("colors/dracula-nocturne.lua", "lua/dracula-nocturne", "lua/lualine/themes/dracula-nocturne.lua")
SPEC = "lua/plugins/dracula-nocturne.lua"


def config_dir() -> Path:
    """stdpath("config"): $XDG_CONFIG_HOME (on Windows too) or ~/.config, %LOCALAPPDATA% on Windows,
    then $NVIM_APPNAME or nvim."""
    windows = system.current() is system.OS.WINDOWS
    base = system.env_dir("XDG_CONFIG_HOME") or (system.local_appdata() if windows else system.config_home())
    return base / (os.environ.get("NVIM_APPNAME") or "nvim")


STARTER = paths.THEMES / "nvim" / "lazyvim"


def same(path: Path, theme_file: Path) -> bool:
    return path.is_file() and theme_file.is_file() and path.read_bytes() == theme_file.read_bytes()


def lazyvim() -> bool:
    """A LazyVim config of the user's own, rather than the starter install puts there."""
    lazy = config_dir() / "lua" / "config" / "lazy.lua"
    ours = same(lazy, STARTER / "lua" / "config" / "lazy.lua")
    return ((config_dir() / "lazyvim.json").exists() or lazy.exists()) and not ours


def theme() -> list[Step]:
    links: list[Step] = [Link(f"nvim/{rel}", config_dir() / rel) for rel in THEME_FILES]
    select = (
        "--level full adds it to LazyVim"
        if lazyvim()
        else 'vim.cmd.colorscheme("dracula-nocturne") in your init.lua, or --level full sets up LazyVim with it'
    )
    return [*links, Note(f"Select it: {select}")]


def starter(files: list[str] | None = None) -> list[Step]:
    files = files or sorted(p.relative_to(STARTER).as_posix() for p in STARTER.rglob("*") if p.is_file())
    return [Copy(f"nvim/lazyvim/{rel}", config_dir() / rel) for rel in files]


def full() -> list[Step]:
    """LazyVim's starter with the colorscheme; into a LazyVim config only the colorscheme's spec."""
    return starter([SPEC]) if lazyvim() else starter()


APP = App(
    id="nvim",
    title="Neovim",
    url="https://neovim.io",
    group=Group.EDITOR,
    binary="nvim",
    platforms=system.EVERYWHERE,
    tiers={
        Level.THEME: Tier("Pierre Dark code on Dracula's editor colours, see-through menus", theme),
        Level.FULL: Tier("LazyVim with the colorscheme, its menus see-through too", full, cleanup=starter),
    },
)
