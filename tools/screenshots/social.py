"""The repository's social preview, 1280 by 640 (GitHub: Settings > Social preview): the name, and
three of the README's scenes as see-through windows side by side, the middle one larger."""

from collections.abc import Callable
from pathlib import Path

from ansi import AnsiHtml
from capture import Home, capture
from frames import CELL, PAD, Frame, png, styles, window
from scenes import SCENES

from nocturne.app import Level
from nocturne.apps import registry

SIZE = (1280, 640)
SHOTS = ["ghostty-full", "nvim-full", "nvim-theme"]  # left, middle (in front), right
COLUMNS = 84  # the same for all three
ROWS = (22, 30)  # the side windows, the middle one (the start screen needs the room)
SCALE = (0.46, 0.56)
MIDDLE = 438  # the line the windows are centred on
# near-black behind the name; glows in the accents behind the windows, for the see-through to show
NIGHT = ",".join([
    *(f"radial-gradient(circle at {at},{c}66 0,transparent 30%)" for c, at in (("#bd93f9", "18% 78%"), ("#ff79c6", "82% 74%"), ("#8be9fd", "50% 105%"))),
    "radial-gradient(circle at 12% 0%,#bd93f933 0,transparent 45%)",
    "#0a0a0a",
])  # fmt: skip


def social(conv: AnsiHtml, home_at: Callable[[Level], Home], dest: Path) -> None:
    p = conv.palette
    apps = len(registry()) // 10 * 10  # "20+": true until the next ten, so a new app needs no new picture
    scenes = {scene.name: scene for scene in SCENES}
    width = COLUMNS * CELL[0] + 2 * PAD[0]
    gap = (SIZE[0] - width * (2 * SCALE[0] + SCALE[1])) / 4
    x = gap
    slots = []
    for i, name in enumerate(SHOTS):
        scene = scenes[name]
        if scene.command is None:
            raise SystemExit(f"{name} is a screenshot by hand, not one to capture")
        h = home_at(scene.level)
        size, scale = (COLUMNS, ROWS[i == 1]), SCALE[i == 1]
        pane = capture(h, scene.command(h), size, scene.keys, scene.wait)
        y = MIDDLE - (size[1] * CELL[1] + 2 * PAD[1]) * scale / 2
        style = f"left:{x:.0f}px;top:{y:.0f}px;transform:scale({scale})"
        slots.append(
            f'<div class="slot" style="{style}">{window(conv, pane, Frame("glass", fill=scene.frame.fill), size)}</div>'
        )
        x += width * scale + gap
    page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0}}
body{{width:{SIZE[0]}px;height:{SIZE[1]}px;overflow:hidden;position:relative;background:{NIGHT};
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
.head{{position:absolute;left:0;right:0;top:52px;text-align:center}}
.name{{font-size:96px;font-weight:800;letter-spacing:-2px;line-height:1.05;color:{p["fg"].hex}}}
.name span{{color:transparent;background:linear-gradient(90deg,{p["purple"].hex},{p["pink"].hex});
  -webkit-background-clip:text;background-clip:text}}
.tag{{font-size:30px;margin-top:10px;color:{p["comment"].hex}}}
.slot{{position:absolute;transform-origin:top left}}
.slot .win{{box-shadow:0 0 0 1px {p["surface"].hex},0 18px 40px rgba(0,0,0,.6)}}
{styles(conv)}
</style></head><body>
<div class="head"><div class="name">Dracula <span>Nocturne</span></div><div class="tag">Dracula, but later at night · {apps}+ apps · one palette</div></div>
{"".join(slots)}</body></html>"""
    png(page, SIZE, dest, scale=1)  # GitHub takes up to 1 MB, at 1280 by 640
