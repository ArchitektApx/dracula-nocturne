"""The palette: palette.toml loaded into named colours, plus the formats templates ask for."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from pathlib import Path

HEX = re.compile(r"#[0-9a-f]{6}")
# Sections whose keys are used without a prefix: {{bg}}, {{purple}}
FLAT = ("base", "accent")


@dataclass(frozen=True)
class Color:
    hex: str

    def __post_init__(self) -> None:
        if not HEX.fullmatch(self.hex):
            raise ValueError(f"not a #rrggbb colour: {self.hex!r}")

    @property
    def rgb(self) -> tuple[int, int, int]:
        h = self.hex
        return int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)

    def alpha(self, a: float) -> str:
        """#rrggbbaa with the alpha as a fraction."""
        return f"{self.hex}{round(a * 255):02x}"

    def mix(self, other: Color, t: float) -> Color:
        """This colour moved by t (0..1) towards other."""
        r, g, b = (round(x + (y - x) * t) for x, y in zip(self.rgb, other.rgb, strict=True))
        return Color(f"#{r:02x}{g:02x}{b:02x}")

    def luminance(self) -> float:
        def lin(c: int) -> float:
            s = c / 255
            return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4  # noqa: PLR2004

        r, g, b = (lin(c) for c in self.rgb)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def contrast(self, other: Color) -> float:
        """WCAG contrast ratio, 1 to 21."""
        a, b = sorted((self.luminance(), other.luminance()), reverse=True)
        return (a + 0.05) / (b + 0.05)


def _rgb(c: Color) -> str:
    return " ".join(map(str, c.rgb))


# Formats for {{name|format}}; plain {{name}} is the #rrggbb hex.
FORMATS: dict[str, Callable[[Color], str]] = {
    "hex": lambda c: c.hex,
    "upper": lambda c: c.hex.upper(),
    "bare": lambda c: c.hex[1:],  # rrggbb
    "rgb": _rgb,  # 189 147 249, for css rgb(... / alpha)
    "rgb_comma": lambda c: ",".join(map(str, c.rgb)),
    "ansi": lambda c: "38;2;" + ";".join(map(str, c.rgb)),  # truecolor SGR foreground
    "ansi_bg": lambda c: "48;2;" + ";".join(map(str, c.rgb)),
    "argb": lambda c: "0xff" + c.hex[1:],  # JankyBorders
}


@dataclass(frozen=True)
class Palette:
    name: str
    colors: dict[str, Color]
    ansi: tuple[Color, ...]

    def __getitem__(self, key: str) -> Color:
        try:
            return self.colors[key]
        except KeyError:
            raise KeyError(f"no colour named {key!r} in the palette") from None

    def section(self, prefix: str) -> dict[str, Color]:
        """All colours of one section, without the prefix: section('syntax')['string']."""
        return {k.removeprefix(prefix + "."): v for k, v in self.colors.items() if k.startswith(prefix + ".")}

    def __iter__(self) -> Iterator[str]:
        return iter(self.colors)

    def format(self, key: str, fmt: str = "hex") -> str:
        if fmt not in FORMATS:
            raise KeyError(f"unknown colour format {fmt!r} (known: {', '.join(FORMATS)})")
        return FORMATS[fmt](self[key])


def load(path: Path) -> Palette:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    colors: dict[str, Color] = {}
    for section, values in data.items():
        if not isinstance(values, dict) or section == "ansi":
            continue
        table = cast("dict[str, object]", values)
        for key, value in table.items():
            name = key if section in FLAT else f"{section}.{key}"
            if name in colors:
                raise ValueError(f"{path.name}: {name!r} is defined twice")
            colors[name] = Color(str(value).lower())
    try:
        ansi = tuple(colors[n] for n in data["ansi"]["colors"])
    except KeyError as e:
        raise ValueError(f"{path.name}: [ansi] names an unknown colour: {e}") from None
    if len(ansi) != 16:  # noqa: PLR2004
        raise ValueError(f"{path.name}: [ansi] needs 16 colours, has {len(ansi)}")
    colors.update({f"ansi.{i}": c for i, c in enumerate(ansi)})
    return Palette(str(data.get("name", "Dracula Nocturne")), colors, ansi)
