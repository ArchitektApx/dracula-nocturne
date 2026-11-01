"""A captured pane in a window, as HTML, and the HTML as a PNG (headless Chrome or Chromium).

window: a solid terminal with a title bar, as a theme alone looks. glass: see-through and blurred
over a wallpaper, no title bar, as the look level makes it (the cursor trail is an animation, so
it isn't drawn). card: a plain
tool output. placeholder: for what still needs a real screenshot.
"""

import html
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from ansi import AnsiHtml
from capture import Pane

from nocturne.palette import Palette

FONT = 14  # px
CELL = (8.43, 19.0)  # px per column and row of MesloLGS Nerd Font Mono at FONT
PAD = (16, 12)  # inside the window
MARGIN = 28  # around it, for the shadow and the wallpaper
TITLE = 30
CHROME = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome", "chromium", "chromium-browser",
]  # fmt: skip


@dataclass
class Frame:
    kind: str  # window, glass, card, placeholder
    title: str = ""
    tabs: tuple[str, ...] = ()  # kitty draws its own tab bar: (active, other, ...)
    fill: str = ""  # a palette colour for cells tmux reports without one (apps that paint every cell)


def _size(cols: int, rows: int, frame: Frame) -> tuple[int, int]:
    extra = TITLE if frame.kind == "window" else 0
    extra += round(CELL[1]) + 6 if frame.tabs else 0
    return round(cols * CELL[0] + 2 * PAD[0] + 2 * MARGIN), round(rows * CELL[1] + 2 * PAD[1] + 2 * MARGIN + extra)


def _tabs(p: Palette, tabs: tuple[str, ...]) -> str:
    def tab(i: int, name: str) -> str:
        bg, fg = (p["pink"].hex, p["bg"].hex) if i == 0 else (p["surface"].hex, p["comment"].hex)
        return f'<span style="background:{bg};color:{fg}"> {i + 1} {html.escape(name)} </span><span style="color:{bg}"></span>'

    return '<div class="tabs">' + "".join(tab(i, n) for i, n in enumerate(tabs)) + "</div>"


def _cursor(p: Palette, pane: Pane) -> str:
    x, y = pane.cursor
    style = f"left:{x * CELL[0]}px;top:{y * CELL[1]}px;width:{CELL[0]}px;height:{CELL[1]}px"
    return f'<b style="{style};background:{p["pink"].hex}"></b>'


# Powerline caps (U+E0B0 to U+E0D7): a terminal stretches them to the full cell height, a browser
# draws them at the font's own height, which leaves them shorter than the coloured cell beside them
CAPS = re.compile("([\ue0b0-\ue0d7]+)")
CAP_SCALE = 1.07


def _caps(body: str) -> str:
    return CAPS.sub(r'<u class="cap">\1</u>', body)


def styles(conv: AnsiHtml) -> str:
    """The CSS every window needs, whichever page it's on."""
    p = conv.palette
    glass_bg = f"rgba({p.format('bg', 'rgb_comma')},.7)"  # the look's background-opacity
    return f"""
.win{{display:inline-block;border-radius:12px;overflow:hidden;position:relative;background:{p["bg"].hex};
  box-shadow:0 0 0 1px {p["surface"].hex},0 12px 30px rgba(0,0,0,.45)}}
.win.glass{{background:{glass_bg};backdrop-filter:blur(20px) saturate(1.2)}}
.bar{{height:{TITLE}px;line-height:{TITLE}px;text-align:center;color:{p["comment"].hex};font:13px -apple-system,system-ui,sans-serif;
  background:{p["surface"].hex};position:relative}}
.dots{{position:absolute;left:12px;top:9px;display:flex;gap:8px}}.dots span{{width:12px;height:12px;border-radius:50%}}
.tabs{{font:{FONT}px/{round(CELL[1]) + 6}px "MesloLGS Nerd Font Mono",monospace;padding:0 {PAD[0]}px;white-space:pre}}
.term{{position:relative;margin:{PAD[1]}px {PAD[0]}px;overflow:hidden}}
pre{{margin:0;color:{p["fg"].hex};font:{FONT}px/{CELL[1]}px "MesloLGS Nerd Font Mono","Symbols Nerd Font",monospace;white-space:pre}}
u.cap{{text-decoration:none;display:inline-block;transform:scaleY({CAP_SCALE})}} i{{font-style:normal;display:inline-block;height:{CELL[1]}px;vertical-align:top}} b{{position:absolute;display:block}}
{conv.stylesheet()}"""


def window(conv: AnsiHtml, pane: Pane, frame: Frame, size: tuple[int, int]) -> str:
    """One window with the pane in it, as HTML (with styles() on the page)."""
    p, (cols, rows) = conv.palette, size
    body = _caps(conv.convert(pane.text.rstrip("\n")))
    glass = frame.kind == "glass"
    bar = ""
    if frame.kind == "window":
        dots = "".join(f'<span style="background:{c}"></span>' for c in ("#ff5f57", "#febc2e", "#28c840"))
        bar = f'<div class="bar"><div class="dots">{dots}</div>{html.escape(frame.title)}</div>'
    tabs = _caps(_tabs(p, frame.tabs)) if frame.tabs else ""
    term = f"{f'background:{p[frame.fill].hex};' if frame.fill else ''}width:{cols * CELL[0]:.0f}px;height:{rows * CELL[1]:.0f}px"
    cursor = _cursor(p, pane) if glass else ""
    return f'<div class="win{" glass" if glass else ""}">{bar}{tabs}<div class="term" style="{term}"><pre>{body}</pre>{cursor}</div></div>'


def page(conv: AnsiHtml, pane: Pane, frame: Frame, size: tuple[int, int]) -> str:
    wall = wallpaper(conv.palette) if frame.kind == "glass" else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;background:transparent}}
body{{padding:{MARGIN}px;{wall}}}
{styles(conv)}
</style></head><body>{window(conv, pane, frame, size)}</body></html>"""


def wallpaper(p: Palette) -> str:
    """A dark wallpaper with soft blobs in the accents, for the see-through to show."""
    blobs = [("purple", "18% 25%"), ("pink", "82% 30%"), ("cyan", "60% 90%")]
    layers = ",".join(f"radial-gradient(circle at {at},{p[c].hex}aa 0,transparent 38%)" for c, at in blobs)
    return f"background:{layers},#1a1026;"


def placeholder(p: Palette, title: str, level: str) -> str:
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;background:transparent}}
div{{margin:{MARGIN}px;height:260px;border:2px dashed {p["line"].hex};border-radius:12px;display:flex;flex-direction:column;
  align-items:center;justify-content:center;font:16px -apple-system,system-ui,sans-serif;color:{p["comment"].hex}}}
strong{{color:{p["purple"].hex};font-size:22px}}
</style></head><body><div><strong>{html.escape(title)}</strong>{html.escape(level)} · screenshot to come</div></body></html>"""


def chrome() -> str | None:
    return next((c for c in CHROME if shutil.which(c) or Path(c).exists()), None)


def png(page_html: str, size: tuple[int, int], dest: Path, scale: int = 2) -> None:
    browser = chrome()
    if browser is None:
        raise SystemExit("needs Google Chrome or Chromium for the PNGs")
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "page.html"
        src.write_text(page_html, encoding="utf-8")
        argv = [
            browser, "--headless", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={tmp}/profile",
            "--default-background-color=00000000", f"--force-device-scale-factor={scale}",
            f"--window-size={size[0]},{size[1]}", f"--screenshot={dest}", src.as_uri(),
        ]  # fmt: skip
        subprocess.run(argv, capture_output=True, check=True, timeout=60)


def render(conv: AnsiHtml, pane: Pane, frame: Frame, size: tuple[int, int], dest: Path) -> None:
    png(page(conv, pane, frame, size), _size(*size, frame), dest)
