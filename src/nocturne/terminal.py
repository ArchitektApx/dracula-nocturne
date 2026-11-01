"""What Ghostty and kitty share, so both terminals come out the same: the colours and the look."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nocturne.palette import Palette

# The look level
OPACITY = 0.7
BLUR = 20
PADDING = (8, 6)  # x, y in points
FONT = "MesloLGS Nerd Font Mono"  # the font Powerlevel10k recommends; any Nerd Font has the icons


def terminal_colors(p: Palette) -> dict[str, str]:
    return {
        "background": p["bg"].hex,
        "foreground": p["fg"].hex,
        "cursor": p["pink"].hex,
        "cursor_text": p["bg"].hex,
        "selection": p["selection"].hex,
        "divider": p["selection"].hex,
    }
