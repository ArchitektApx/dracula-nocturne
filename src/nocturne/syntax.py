"""Pierre Dark's token rules (data/pierre-dark.json), recoloured from the palette's [syntax].

The JSON keeps Pierre's original colours. Each one that belongs to a [syntax] role is swapped
for the palette's current value, so changing `string` in palette.toml changes every string rule
in VS Code, bat and yazi.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, cast

from nocturne import paths

if TYPE_CHECKING:
    from nocturne.palette import Palette

# Pierre Dark's colour for each [syntax] role
PIERRE = {
    "text": "#fafafa",
    "comment": "#737373",
    "string": "#5ecc71",
    "regexp": "#64d1db",
    "escape": "#61d5c0",
    "number": "#68cdf2",
    "constant": "#ffd452",
    "keyword": "#ff678d",
    "operator": "#636363",
    "func": "#9d6afb",
    "type": "#d568ea",
    "variable": "#ffa359",
    "parameter": "#a3a3a3",
    "builtin": "#ffab16",
    "enum_member": "#08c0ef",
    "decorator": "#69b1ff",
    "tag": "#ff855e",
    "attribute": "#60d199",
}


def pierre() -> dict[str, Any]:
    return cast("dict[str, Any]", json.loads((paths.DATA / "pierre-dark.json").read_text(encoding="utf-8")))


def recolor(value: Any, palette: Palette) -> Any:  # noqa: ANN401
    """value with every Pierre syntax colour replaced by the palette's, alpha kept."""
    roles = {hex_: palette[f"syntax.{role}"].hex for role, hex_ in PIERRE.items()}
    if isinstance(value, dict):
        return {k: recolor(v, palette) for k, v in cast("dict[str, Any]", value).items()}
    if isinstance(value, list):
        return [recolor(v, palette) for v in cast("list[Any]", value)]
    if isinstance(value, str) and value.startswith("#") and value[:7].lower() in roles:
        return roles[value[:7].lower()] + value[7:]
    return value


def token_colors(palette: Palette) -> list[dict[str, Any]]:
    return cast("list[dict[str, Any]]", recolor(pierre()["tokenColors"], palette))


def semantic_token_colors(palette: Palette) -> dict[str, Any]:
    return cast("dict[str, Any]", recolor(pierre()["semanticTokenColors"], palette))
