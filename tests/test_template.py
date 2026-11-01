import pytest

from nocturne.palette import Palette
from nocturne.template import TemplateError, render


def test_render(palette: Palette):
    assert render("a {{purple}} b {{purple|rgb}}", palette) == "a #bd93f9 b 189 147 249"


def test_unknown_name_points_at_the_line(palette: Palette):
    with pytest.raises(TemplateError, match=r"x\.conf:2: no colour named 'purpel'"):
        render("ok\n{{purpel}}", palette, "x.conf")


def test_other_template_languages_are_left_alone(palette: Palette):
    # oh-my-posh (Go templates) and Lua tables share the braces
    text = '{{ .Path }}{{ if .Root }}x{{ end }} {{.Parent}} t = {{ fg = "x" }}'
    assert render(text, palette) == text
