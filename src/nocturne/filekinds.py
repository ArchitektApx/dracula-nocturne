"""The file kinds eza and LS_COLORS colour alike, so ls, eza, fd and completion menus agree."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nocturne.palette import Palette

# (eza filekind, LS_COLORS code, colour, bold). LS_COLORS has no "normal" and eza no setuid & co.
FILEKINDS: list[tuple[str | None, str | None, str, bool]] = [
    ("normal", None, "fg", False),
    ("directory", "di", "purple", True),
    ("symlink", "ln", "cyan", False),
    ("pipe", "pi", "yellow", False),
    ("block_device", "bd", "orange", False),
    ("char_device", "cd", "orange", False),
    ("socket", "so", "pink", False),
    ("special", None, "pink", False),
    ("executable", "ex", "green", True),
    ("mount_point", None, "cyan", True),
]
# LS_COLORS only: broken links in red, like eza's broken_symlink
EXTRA = [("or", "red"), ("mi", "red")]
# and dark text on a coloured block for the dangerous permission bits
BLOCKS = [("su", "red"), ("sg", "cyan"), ("tw", "green"), ("ow", "yellow")]

# BSD ls (macOS) reads LSCOLORS instead: one letter pair (text, background) per kind, in this
# order, from the 8 basic terminal colours. Upper case is bold. The terminal themes make
# blue (e) purple and magenta (f) pink, so this comes out the same as LS_COLORS, with yellow
# standing in for orange. di ln so pi ex bd cd su sg tw ow
LSCOLORS = "Exgxfxdxcxdxdxabagacad"


def ls_colors(p: Palette) -> str:
    parts = [f"{code}={'1;' if bold else ''}{p.format(color, 'ansi')}" for _, code, color, bold in FILEKINDS if code]
    parts += [f"{code}={p.format(color, 'ansi')}" for code, color in EXTRA]
    parts += [f"{code}={p.format('bg', 'ansi')};{p.format(color, 'ansi_bg')}" for code, color in BLOCKS]
    return ":".join(parts)
