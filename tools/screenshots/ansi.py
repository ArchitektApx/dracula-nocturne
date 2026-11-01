"""Terminal output with ANSI colours (truecolor, 256 and 16) as HTML spans; everything else is dropped."""

import html
import re
from dataclasses import dataclass, field

from nocturne.palette import Palette

SGR = re.compile(r"(\x1b\[[0-9;]*m)")
CUBE = [0, 95, 135, 175, 215, 255]


@dataclass
class Pen:
    fg: str | None = None
    bg: str | None = None
    bold: bool = False
    dim: bool = False
    reverse: bool = False

    def css(self, default_fg: str, default_bg: str) -> str:
        fg, bg = (self.bg or default_bg, self.fg or default_fg) if self.reverse else (self.fg, self.bg)
        parts = [
            fg and f"color:{fg}",
            bg and f"background:{bg}",
            self.bold and "font-weight:700",
            self.dim and "opacity:.6",
        ]
        return ";".join(p for p in parts if p)


@dataclass
class AnsiHtml:
    palette: Palette
    classes: dict[str, str] = field(default_factory=dict)  # css -> class name, shared by every capture

    def color(self, n: int) -> str:
        if n < 16:
            return self.palette.ansi[n].hex
        if n < 232:
            n -= 16
            return f"#{CUBE[n // 36]:02x}{CUBE[n // 6 % 6]:02x}{CUBE[n % 6]:02x}"
        v = 8 + (n - 232) * 10
        return f"#{v:02x}{v:02x}{v:02x}"

    def _extended(self, codes: list[int], i: int) -> tuple[str | None, int]:
        """38;2;r;g;b or 38;5;n at codes[i]: the colour and how many codes it used."""
        if i + 4 < len(codes) and codes[i + 1] == 2:
            return "#{:02x}{:02x}{:02x}".format(*codes[i + 2 : i + 5]), 4
        if i + 2 < len(codes) and codes[i + 1] == 5:
            return self.color(codes[i + 2]), 2
        return None, 0

    def _apply(self, pen: Pen, codes: list[int]) -> Pen:
        i = 0
        while i < len(codes):
            c = codes[i]
            if c == 0:
                pen = Pen()
            elif c in (1, 2, 7):
                setattr(pen, {1: "bold", 2: "dim", 7: "reverse"}[c], True)
            elif c == 22:
                pen.bold = pen.dim = False
            elif c == 27:
                pen.reverse = False
            elif c in (38, 48):
                color, used = self._extended(codes, i)
                setattr(pen, "fg" if c == 38 else "bg", color)
                i += used
            elif c in (39, 49):
                setattr(pen, "fg" if c == 39 else "bg", None)
            elif 30 <= c <= 37 or 90 <= c <= 97:
                pen.fg = self.color(c - 30 if c < 90 else c - 90 + 8)
            elif 40 <= c <= 47 or 100 <= c <= 107:
                pen.bg = self.color(c - 40 if c < 100 else c - 100 + 8)
            i += 1
        return pen

    def convert(self, text: str) -> str:
        """tmux writes every captured line from the default colours, so each line starts afresh."""
        return "\n".join(self._line(line) for line in text.split("\n"))

    def _line(self, line: str) -> str:
        pen = Pen()
        out: list[str] = []
        for part in SGR.split(line):
            if part.startswith("\x1b["):
                pen = self._apply(pen, [int(c) if c else 0 for c in part[2:-1].split(";")])
            elif part:
                css = pen.css(self.palette["fg"].hex, self.palette["bg"].hex)
                name = self.classes.setdefault(css, f"s{len(self.classes)}") if css else ""
                out.append(f'<i class="{name}">{html.escape(part)}</i>' if css else html.escape(part))
        return "".join(out)

    def stylesheet(self) -> str:
        return "".join(f".{name}{{{css}}}" for css, name in self.classes.items())
