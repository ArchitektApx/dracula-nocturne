import re
from pathlib import Path

import pytest

from nocturne.palette import Color, Palette, load
from nocturne.preview import contrast_report, render


def test_names_and_sections(palette: Palette):
    assert palette["purple"].hex == "#bd93f9"
    assert palette["bright.red"].hex == "#ff6e6e"
    assert palette["ansi.0"] == palette["surface"]
    assert "string" in palette.section("syntax")
    assert len(palette.ansi) == 16


def test_formats(palette: Palette):
    assert palette.format("purple", "rgb") == "189 147 249"
    assert palette.format("purple", "argb") == "0xffbd93f9"
    assert palette.format("purple", "ansi") == "38;2;189;147;249"
    assert palette.format("bg", "upper") == "#0A0A0A"
    with pytest.raises(KeyError, match="unknown colour format"):
        palette.format("purple", "cmyk")
    with pytest.raises(KeyError, match="no colour named"):
        palette.format("purpel")


def test_color_math():
    black, white = Color("#000000"), Color("#ffffff")
    assert black.contrast(white) == pytest.approx(21)
    assert black.mix(white, 0.5).hex == "#808080"
    assert Color("#bd93f9").alpha(0.5) == "#bd93f980"
    with pytest.raises(ValueError, match="#rrggbb"):
        Color("bd93f9")


def test_bad_palettes(tmp_path: Path):
    p = tmp_path / "palette.toml"
    p.write_text('[base]\nbg = "#000000"\n[ansi]\ncolors = ["bg"]\n')
    with pytest.raises(ValueError, match="16 colours"):
        load(p)
    p.write_text('[base]\nbg = "#000000"\n[ansi]\ncolors = ["nope"]\n')
    with pytest.raises(ValueError, match="unknown colour"):
        load(p)


@pytest.mark.parametrize("pair", range(16))
def test_contrast_floors(palette: Palette, pair: int):
    a, b, ratio, floor = contrast_report(palette)[pair]
    assert ratio >= floor, f"{a} on {b}: {ratio:.2f} < {floor}"


def test_preview_renders(palette: Palette):
    out = render(palette)
    assert "Dracula Nocturne" in out
    assert not re.search(r"\blow\b", out)
