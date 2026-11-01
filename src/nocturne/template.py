"""{{name}} and {{name|format}} placeholders, filled from the palette."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nocturne.palette import Palette

PLACEHOLDER = re.compile(r"\{\{([a-z][a-zA-Z0-9_.]*)(?:\|([a-z_]+))?\}\}")


class TemplateError(ValueError):
    pass


def render(text: str, palette: Palette, source: str = "<template>") -> str:
    def sub(m: re.Match[str]) -> str:
        try:
            return palette.format(m.group(1), m.group(2) or "hex")
        except KeyError as e:
            line = text.count("\n", 0, m.start()) + 1
            raise TemplateError(f"{source}:{line}: {e.args[0]}") from None

    return PLACEHOLDER.sub(sub, text)


def header(palette: Palette, app: str, comment: str = "#") -> str:
    """The first line of every generated theme file."""
    return (
        f"{comment} {palette.name} for {app}. Generated from palette.toml by `nocturne build`: edit that, not this.\n"
    )
