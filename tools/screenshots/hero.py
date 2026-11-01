"""assets/hero.svg: the name and the tagline as on the social preview, and the palette as one bar,
drawn from palette.toml and framed like a window under JankyBorders."""

from nocturne.palette import Palette

SWATCHES = ["bg", "surface", "selection", "comment", "fg", "purple", "pink", "cyan", "green", "yellow", "orange", "red"]
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
WIDTH, HEIGHT = 880, 214
BAR = (70, 152, WIDTH - 140, 14)  # x, y, width, height
# where "Nocturne" sits, roughly, for its gradient (a gradient on part of a text spans the whole text)
NOCTURNE = (450, 680)


def hero(p: Palette) -> str:
    x, y, w, h = BAR
    step = w / len(SWATCHES)
    segments = "".join(
        f'<rect x="{x + i * step:.1f}" y="{y}" width="{step + 0.5:.1f}" height="{h}" fill="{p[n].hex}"><title>{n} {p[n].hex}</title></rect>'
        for i, n in enumerate(SWATCHES)
    )
    first, rest = p.name.split(" ", 1) if " " in p.name else (p.name, "")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <defs>
    <linearGradient id="name" gradientUnits="userSpaceOnUse" x1="{NOCTURNE[0]}" x2="{NOCTURNE[1]}"><stop offset="0" stop-color="{p["purple"].hex}"/><stop offset="1" stop-color="{p["pink"].hex}"/></linearGradient>
    <radialGradient id="glow1" cx="12%" cy="0%" r="60%"><stop offset="0" stop-color="{p["purple"].hex}" stop-opacity=".2"/><stop offset="1" stop-color="{p["purple"].hex}" stop-opacity="0"/></radialGradient>
    <radialGradient id="glow2" cx="100%" cy="100%" r="60%"><stop offset="0" stop-color="{p["pink"].hex}" stop-opacity=".15"/><stop offset="1" stop-color="{p["pink"].hex}" stop-opacity="0"/></radialGradient>
    <linearGradient id="border" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p["purple"].hex}"/><stop offset="1" stop-color="{p["pink"].hex}"/></linearGradient>
    <clipPath id="card"><rect width="{WIDTH}" height="{HEIGHT}" rx="20"/></clipPath>
    <clipPath id="bar"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}"/></clipPath>
  </defs>
  <g clip-path="url(#card)">
    <rect width="{WIDTH}" height="{HEIGHT}" fill="{p["bg"].hex}"/>
    <rect width="{WIDTH}" height="{HEIGHT}" fill="url(#glow1)"/>
    <rect width="{WIDTH}" height="{HEIGHT}" fill="url(#glow2)"/>
  </g>
  <text x="50%" y="88" text-anchor="middle" font-family="{FONT}" font-size="52" font-weight="800" letter-spacing="-1.5"><tspan fill="{p["fg"].hex}">{first} </tspan><tspan fill="url(#name)">{rest}</tspan></text>
  <text x="50%" y="124" text-anchor="middle" font-family="{FONT}" font-size="19" fill="{p["comment"].hex}">Dracula, but later at night</text>
  <g clip-path="url(#bar)">{segments}</g>
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="none" stroke="url(#border)" stroke-width="1.5"/>
</svg>
"""
