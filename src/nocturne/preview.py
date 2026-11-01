"""`nocturne preview`: the palette in the terminal, a code sample, and a contrast report."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nocturne.palette import Color, Palette

RESET = "\033[0m"

# (text, background, minimum WCAG ratio): pairs that have to stay readable
CONTRAST = [
    ("fg", "bg", 7.0),
    ("fg", "surface", 7.0),
    ("fg", "selection", 4.5),
    ("fg", "editor.bg", 7.0),
    ("comment", "bg", 3.0),
    ("comment", "surface", 2.5),
    ("purple", "bg", 4.5),
    ("pink", "bg", 4.5),
    ("bg", "purple", 4.5),
    ("bg", "pink", 4.5),
    ("bg", "orange", 4.5),
    ("syntax.text", "editor.bg", 7.0),
    ("syntax.comment", "editor.bg", 3.0),
    ("syntax.keyword", "editor.bg", 4.5),
    ("syntax.string", "editor.bg", 4.5),
    ("syntax.func", "editor.bg", 3.0),
]


def fg(c: Color) -> str:
    return "\033[38;2;{};{};{}m".format(*c.rgb)


def bg(c: Color) -> str:
    return "\033[48;2;{};{};{}m".format(*c.rgb)


def contrast_report(p: Palette) -> list[tuple[str, str, float, float]]:
    return [(a, b, p[a].contrast(p[b]), floor) for a, b, floor in CONTRAST]


def _swatches(p: Palette, names: list[str]) -> str:
    rows: list[str] = []
    for name in names:
        c = p[name]
        rows.append(f"  {bg(c)}      {RESET} {fg(c)}{name:<14}{RESET}{fg(p['comment'])}{c.hex}{RESET}")
    return "\n".join(rows)


# The code sample as (syntax role, text) runs; one inner list per line
SAMPLE: list[list[tuple[str, str]]] = [
    [("comment", "# a little bit of everything")],
    [("decorator", "@dataclass")],
    [("keyword", "class "), ("type", "Bat"), ("operator", ":")],
    [("text", "    "), ("variable", "name"), ("operator", ": "), ("builtin", "str"), ("operator", " = "),
     ("string", '"Nocturne'), ("escape", "\\n"), ("string", '"')],
    [("text", "    "), ("variable", "wings"), ("operator", ": "), ("builtin", "int"), ("operator", " = "),
     ("number", "2")],
    [],
    [("text", "    "), ("keyword", "def "), ("func", "fly"), ("operator", "("), ("builtin", "self"),
     ("operator", ", "), ("parameter", "height"), ("operator", "):")],
    [("text", "        "), ("keyword", "return "), ("func", "match"), ("operator", "("), ("regexp", 'r"^up+$"'),
     ("operator", ", "), ("parameter", "height"), ("operator", ") "), ("keyword", "or "), ("constant", "MAX_HEIGHT")],
]  # fmt: skip


def sample(p: Palette) -> str:
    syntax = p.section("syntax")
    lines = ["".join(f"{fg(syntax[role])}{text}" for role, text in runs) for runs in SAMPLE]
    width = max(len("".join(t for _, t in runs)) for runs in SAMPLE) + 2
    out: list[str] = []
    for runs, line in zip(SAMPLE, lines, strict=True):
        pad = " " * (width - len("".join(t for _, t in runs)))
        out.append(f"  {bg(p['editor.bg'])} {line}{pad}{RESET}")
    return "\n".join(out)


def render(p: Palette) -> str:
    base = ["bg", "surface", "selection", "line", "comment", "fg_dim", "fg", "white"]
    accents = ["purple", "pink", "cyan", "green", "yellow", "orange", "red"]
    ansi = (
        "".join(f"{bg(c)}{i:^4}{RESET}" for i, c in enumerate(p.ansi[:8]))
        + "\n  "
        + "".join(f"{bg(c)}{i:^4}{RESET}" for i, c in enumerate(p.ansi[8:], 8))
    )
    out = [
        f"\n  {fg(p['purple'])}{p.name}{RESET}\n",
        _swatches(p, base),
        "",
        _swatches(p, accents),
        f"\n  {fg(p['comment'])}terminal colours{RESET}\n  {ansi}\n",
        f"  {fg(p['comment'])}code{RESET}",
        sample(p),
        f"\n  {fg(p['comment'])}contrast (WCAG){RESET}",
    ]
    for a, b, ratio, floor in contrast_report(p):
        mark = f"{fg(p['green'])}ok{RESET}" if ratio >= floor else f"{fg(p['red'])}low{RESET}"
        out.append(f"  {bg(p[b])}{fg(p[a])} Aa {RESET} {a:<15} on {b:<10} {ratio:5.2f}  {mark}")
    return "\n".join(out) + "\n"
