"""A TextMate theme (bat, yazi's previews) from Pierre Dark's token rules, as in VS Code."""

from __future__ import annotations

import plistlib
from typing import TYPE_CHECKING, Any

from nocturne.syntax import token_colors

if TYPE_CHECKING:
    from nocturne.palette import Palette


def tmtheme(p: Palette) -> str:
    rules: list[dict[str, Any]] = [
        {
            "settings": {
                "background": p["bg"].hex,
                "foreground": p["syntax.text"].hex,
                "caret": p["pink"].hex,
                "selection": p["selection"].hex,
                "lineHighlight": p["editor.line_highlight"].hex,
                "gutter": p["bg"].hex,
                "gutterForeground": p["editor.line_nr"].hex,
                "invisibles": p["line"].hex,
                "findHighlight": p["orange"].hex,
                "findHighlightForeground": p["bg"].hex,
            }
        }
    ]
    for rule in token_colors(p):
        scope: str | list[str] | None = rule.get("scope")
        settings = {k: v for k, v in rule["settings"].items() if k in {"foreground", "background", "fontStyle"}}
        if not scope or not settings:
            continue
        entry: dict[str, Any] = {"scope": ", ".join(scope) if isinstance(scope, list) else scope, "settings": settings}
        if "name" in rule:
            entry["name"] = rule["name"]
        rules.append(entry)
    # bat's diff markers in the gutter (--style=changes) use these scopes
    rules += [
        {"scope": "markup.inserted", "settings": {"foreground": p["green"].hex}},
        {"scope": "markup.deleted", "settings": {"foreground": p["red"].hex}},
        {"scope": "markup.changed", "settings": {"foreground": p["orange"].hex}},
    ]
    data = {
        "name": p.name,
        "author": "ArchitektApx",
        "comment": "Generated from palette.toml by `nocturne build`: edit that, not this.",
        "semanticClass": "theme.dark.dracula-nocturne",
        "settings": rules,
    }
    return plistlib.dumps(data, sort_keys=False).decode()
