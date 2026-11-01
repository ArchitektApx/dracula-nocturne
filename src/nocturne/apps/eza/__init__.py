"""eza: file colours from the table it shares with LS_COLORS (nocturne/filekinds.py), plus its own."""

from __future__ import annotations

from typing import TYPE_CHECKING

from nocturne import system
from nocturne.app import App, Group, Level, Tier
from nocturne.filekinds import FILEKINDS
from nocturne.steps import Link, Note
from nocturne.template import header, render

if TYPE_CHECKING:
    from pathlib import Path

    from nocturne.palette import Palette

REST = """\
perms:
  user_read: {foreground: "{{yellow}}"}
  user_write: {foreground: "{{red}}"}
  user_execute_file: {foreground: "{{green}}"}
  user_execute_other: {foreground: "{{green}}"}
  group_read: {foreground: "{{yellow}}", is_dimmed: true}
  group_write: {foreground: "{{red}}", is_dimmed: true}
  group_execute: {foreground: "{{green}}", is_dimmed: true}
  other_read: {foreground: "{{comment}}"}
  other_write: {foreground: "{{comment}}"}
  other_execute: {foreground: "{{comment}}"}
  special_user_file: {foreground: "{{pink}}"}
  special_other: {foreground: "{{pink}}"}
  attribute: {foreground: "{{comment}}"}

size:
  major: {foreground: "{{cyan}}"}
  minor: {foreground: "{{cyan}}"}
  number_byte: {foreground: "{{fg}}"}
  number_kilo: {foreground: "{{cyan}}"}
  number_mega: {foreground: "{{purple}}"}
  number_giga: {foreground: "{{pink}}"}
  number_huge: {foreground: "{{red}}"}
  unit_byte: {foreground: "{{comment}}"}
  unit_kilo: {foreground: "{{comment}}"}
  unit_mega: {foreground: "{{comment}}"}
  unit_giga: {foreground: "{{comment}}"}
  unit_huge: {foreground: "{{comment}}"}

users:
  user_you: {foreground: "{{pink}}"}
  user_root: {foreground: "{{red}}", is_bold: true}
  user_other: {foreground: "{{comment}}"}
  group_yours: {foreground: "{{purple}}"}
  group_other: {foreground: "{{comment}}"}
  group_root: {foreground: "{{red}}"}

links:
  normal: {foreground: "{{cyan}}"}
  multi_link_file: {foreground: "{{orange}}"}

git:
  new: {foreground: "{{green}}"}
  modified: {foreground: "{{orange}}"}
  deleted: {foreground: "{{red}}"}
  renamed: {foreground: "{{cyan}}"}
  typechange: {foreground: "{{pink}}"}
  ignored: {foreground: "{{comment}}"}
  conflicted: {foreground: "{{red}}", is_bold: true}

git_repo:
  branch_main: {foreground: "{{green}}"}
  branch_other: {foreground: "{{pink}}"}
  git_clean: {foreground: "{{green}}"}
  git_dirty: {foreground: "{{orange}}"}

file_type:
  image: {foreground: "{{pink}}"}
  video: {foreground: "{{pink}}"}
  music: {foreground: "{{cyan}}"}
  lossless: {foreground: "{{cyan}}"}
  crypto: {foreground: "{{green}}"}
  document: {foreground: "{{yellow}}"}
  compressed: {foreground: "{{orange}}"}
  temp: {foreground: "{{comment}}"}
  compiled: {foreground: "{{comment}}"}
  build: {foreground: "{{yellow}}", is_underline: true}
  source: {foreground: "{{yellow}}"}

punctuation: {foreground: "{{comment}}"}
date: {foreground: "{{cyan}}"}
inode: {foreground: "{{comment}}"}
blocks: {foreground: "{{comment}}"}
header: {foreground: "{{purple}}", is_underline: true}
octal: {foreground: "{{pink}}"}
flags: {foreground: "{{comment}}"}
control_char: {foreground: "{{red}}"}
broken_symlink: {foreground: "{{red}}", is_underline: true}
broken_path_overlay: {is_underline: true}
"""


def generate(p: Palette) -> dict[str, str]:
    lines = [header(p, "eza").rstrip("\n"), "filekinds:"]
    for kind, _, color, bold in FILEKINDS:
        if kind:
            lines.append(f'  {kind}: {{foreground: "{p[color].hex}"{", is_bold: true" if bold else ""}}}')
    return {"theme.yml": "\n".join(lines) + "\n\n" + render(REST, p, "eza")}


def config_dir() -> Path:
    """EZA_CONFIG_DIR, else the OS's config folder (Application Support on macOS, whatever its man page says)."""
    return system.env_dir("EZA_CONFIG_DIR") or system.native_config() / "eza"


APP = App(
    id="eza",
    title="eza",
    url="https://eza.rocks",
    group=Group.TOOL,
    binary="eza",
    platforms=system.EVERYWHERE,
    generate=generate,
    tiers={
        Level.THEME: Tier(
            "file colours, permissions, git status",
            lambda: [
                Link("eza/theme.yml", config_dir() / "theme.yml"),
                Note("A LS_COLORS your shell sets wins over these colours: install ls_colors too, and they match."),
            ],
        ),
    },
)
