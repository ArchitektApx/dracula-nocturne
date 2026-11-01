"""The generated themes: up to date, parseable and consistent with each other."""

import json
import os
import plistlib
import re
import shutil
import subprocess
import sys
import tomllib
from dataclasses import replace
from pathlib import Path

import pytest
import yaml

from nocturne import build, paths
from nocturne.apps import every
from nocturne.filekinds import ls_colors
from nocturne.palette import Color, Palette
from nocturne.steps import Copy


def test_committed_themes_are_up_to_date():
    assert build.stale() == [], "run: uv run nocturne build"


def test_build_is_deterministic(palette: Palette, files: dict[str, str]):
    assert build.outputs(palette) == files


def test_build_writes_everything(tmp_path: Path):
    written = build.build(tmp_path / "themes")
    assert build.stale(tmp_path / "themes") == []
    assert len(written) >= 20


def _by_suffix(files: dict[str, str], *suffixes: str) -> list[str]:
    return [rel for rel in files if rel.endswith(suffixes)]


def test_json(files: dict[str, str]):
    for rel in _by_suffix(files, ".json"):
        json.loads(files[rel])


def test_toml(files: dict[str, str]):
    for rel in _by_suffix(files, ".toml"):
        tomllib.loads(files[rel])


def test_yaml(files: dict[str, str]):
    for rel in _by_suffix(files, ".yml"):
        assert isinstance(yaml.safe_load(files[rel]), dict)


def test_plist(files: dict[str, str]):
    for rel in _by_suffix(files, ".tmTheme", ".xml"):
        theme = plistlib.loads(files[rel].encode())
        assert theme["settings"][0]["settings"]["background"]


SHELLS = {
    ".sh": ["bash", "-n"],
    ".zsh": ["zsh", "-n"],
    ".fish": ["fish", "--no-execute"],
    ".lua": ["luac", "-p", "-"],
    ".ps1": ["pwsh", "-NoProfile", "-Command", "[ScriptBlock]::Create([Console]::In.ReadToEnd()) | Out-Null"],
}


def unix_shell(name: str) -> bool:
    """A zsh, bash or fish to test with. On Windows, nocturne writes no lines for them, and the bash
    on PATH is often only WSL's launcher, without a Linux to start."""
    return sys.platform != "win32" and shutil.which(name) is not None


@pytest.mark.parametrize("suffix", SHELLS)
def test_scripts_parse(files: dict[str, str], suffix: str):
    argv = SHELLS[suffix]
    if not (shutil.which(argv[0]) if argv[0] in {"luac", "pwsh"} else unix_shell(argv[0])):
        pytest.skip(f"{argv[0]} not installed")
    for rel in _by_suffix(files, suffix):
        r = subprocess.run(argv, input=files[rel], capture_output=True, text=True, check=False)
        assert r.returncode == 0, f"{rel}: {r.stderr}"


def test_no_placeholders_left(files: dict[str, str]):
    for rel, content in files.items():
        assert not re.search(r"\{\{[a-z][a-zA-Z0-9_.]*(\|[a-z_]+)?\}\}", content), rel


# Starting points that install copies for the user to change, so they don't say "edit that, not this"
STARTERS = ("nvim/lazyvim/", "p10k/p10k.zsh", "yazi/theme.toml", "ghostty/shaders/")


def test_header_on_every_theme(files: dict[str, str]):
    for rel, content in files.items():
        if rel.endswith((".json", "tmTheme", ".xml", "LICENSE")) or rel.startswith(STARTERS):
            continue  # no comments in JSON; plists say it in their "comment" key
        assert "nocturne build" in content[:600], rel


def test_ghostty_and_kitty_match(palette: Palette, files: dict[str, str]):
    ghostty = dict(line.split(" = ", 1) for line in files["ghostty/dracula-nocturne"].splitlines() if " = " in line)
    kitty = dict(line.split(" ", 1) for line in files["kitty/dracula-nocturne.conf"].splitlines() if line[:1].isalpha())
    gh_palette = [
        line.split("=")[-1] for line in files["ghostty/dracula-nocturne"].splitlines() if line.startswith("palette")
    ]
    assert gh_palette == [kitty[f"color{i}"] for i in range(16)] == [c.hex for c in palette.ansi]
    assert ghostty["background"] == kitty["background"]
    assert ghostty["foreground"] == kitty["foreground"]
    assert ghostty["cursor-color"] == kitty["cursor"]
    assert ghostty["selection-background"] == kitty["selection_background"]
    # selected text keeps its own colours in both
    assert ghostty["selection-foreground"] == "cell-foreground"
    assert kitty["selection_foreground"] == "none"
    assert ghostty["split-divider-color"] == kitty["inactive_border_color"].split()[0]


def test_eza_and_ls_colors_agree(palette: Palette, files: dict[str, str]):
    eza = yaml.safe_load(files["eza/theme.yml"])["filekinds"]
    lsc = dict(part.split("=") for part in ls_colors(palette).split(":"))
    for kind, code in [("directory", "di"), ("symlink", "ln"), ("executable", "ex"), ("socket", "so")]:
        hex_ = eza[kind]["foreground"]
        assert lsc[code].endswith(palette.format(_name(palette, hex_), "ansi")), kind
    assert lsc["ow"] in files["ls_colors/ls_colors.fish"]


def _name(palette: Palette, hex_: str) -> str:
    return next(k for k in palette if palette[k].hex == hex_ and "." not in k)


def test_syntax_colours_follow_the_palette(palette: Palette):
    """Changing [syntax] in palette.toml reaches VS Code and bat, which start from Pierre Dark."""
    colors = dict(palette.colors)
    colors["syntax.string"] = Color("#123456")
    changed = build.outputs(replace(palette, colors=colors))
    assert "#123456" in changed["vscode/themes/dracula-nocturne-color-theme.json"]
    assert "#123456" in changed["bat/Dracula Nocturne.tmTheme"]
    assert "#123456" in changed["nvim/lua/dracula-nocturne/palette.lua"]
    assert palette["syntax.string"].hex not in changed["bat/Dracula Nocturne.tmTheme"]


def test_vscode_terminal_uses_the_ansi_colours(palette: Palette, files: dict[str, str]):
    colors = json.loads(files["vscode/themes/dracula-nocturne-color-theme.json"])["colors"]
    assert colors["terminal.ansiBlack"] == palette.ansi[0].hex
    assert colors["terminal.ansiBrightWhite"] == palette.ansi[15].hex


@pytest.mark.usefixtures("home")
def test_theme_folder_is_what_install_expects():
    for app in every():
        for step in app.steps():
            if isinstance(step, Copy):
                assert (paths.THEMES / step.src).exists(), f"{app.id}: {step.src}"


@pytest.mark.skipif(not shutil.which("tmux"), reason="tmux not installed")
def test_tmux_loads_the_theme_twice():
    """tmux accepts every line, and a reload (bind r) doesn't blank the tab bar."""
    conf = str(paths.THEMES / "tmux" / "dracula-nocturne.conf")
    # -L: a private server; a socket path under pytest's tmp_path is too long for macOS
    tmux = ["tmux", "-L", f"nocturne-test-{os.getpid()}", "-f", "/dev/null"]
    start = subprocess.run([*tmux, "new-session", "-d", "-x", "120", "-y", "30"], capture_output=True, check=False)
    if start.returncode:
        pytest.skip("can't start a tmux server here (sandbox?)")
    try:
        for _ in range(2):
            r = subprocess.run([*tmux, "source-file", conf], capture_output=True, text=True, check=False)
            assert r.returncode == 0, r.stderr
        fmt = subprocess.run([*tmux, "show", "-gv", "status-format[1]"], capture_output=True, text=True, check=True)
        assert "status-left" in fmt.stdout
    finally:
        subprocess.run([*tmux, "kill-server"], check=False)


@pytest.mark.skipif(not unix_shell("bash"), reason="bash not installed")
def test_fzf_keeps_the_users_options_and_adds_itself_once():
    script = f"""
        export FZF_DEFAULT_OPTS="--prompt='> ' --border=none"
        . {paths.THEMES / "fzf" / "fzf.sh"}
        . {paths.THEMES / "fzf" / "fzf.sh"}
        printf '%s' "$FZF_DEFAULT_OPTS"
    """
    opts = subprocess.run(["bash", "-c", script], capture_output=True, text=True, check=True).stdout
    assert opts.count("--color=") == 1
    # fzf takes the last value of an option, so the user's own come last
    assert opts.endswith("--prompt='> ' --border=none")


def test_t3_theme_is_a_complete_export(palette: Palette, files: dict[str, str]):
    theme = json.loads(files["t3code/dracula-nocturne.json"])
    assert theme["version"] == 1
    assert theme["appearance"] == "dark"
    assert theme["colors"] == {k: v.hex for k, v in palette.section("ui").items()}
    assert len(theme["colors"]) == 61  # every role of T3's theme editor


def test_zen_user_js_sets_the_colours(palette: Palette, files: dict[str, str]):
    prefs = dict(re.findall(r'user_pref\("([^"]+)",\s*(.+?)\);', files["zen/user.js"]))
    assert prefs["zen.theme.accent-color"] == f'"{palette["purple"].hex}"'
    assert prefs["better_findbar.custom_text_color"] == f'"{palette["fg"].hex}"'


@pytest.mark.skipif(not shutil.which("nvim"), reason="nvim not installed")
def test_nvim_colorscheme_loads():
    lua = (
        f"vim.opt.rtp:prepend([[{paths.THEMES / 'nvim'}]]); vim.cmd.colorscheme('dracula-nocturne');"
        "local n = vim.api.nvim_get_hl(0, { name = 'NormalFloat' }); io.write(vim.g.colors_name, ' ', tostring(n.bg))"
    )
    r = subprocess.run(
        ["nvim", "--clean", "--headless", "-c", f"lua {lua}", "-c", "qa!"], capture_output=True, text=True, check=False
    )
    assert r.returncode == 0, r.stderr
    assert (r.stdout + r.stderr).strip() == "dracula-nocturne nil"  # floats are see-through by default


def test_ghostty_and_kitty_share_the_look(files: dict[str, str]):
    ghostty = dict(line.split(" = ", 1) for line in files["ghostty/look.ghostty"].splitlines() if " = " in line)
    kitty = dict(line.split(" ", 1) for line in files["kitty/look.conf"].splitlines() if line[:1].isalpha())
    assert ghostty["background-opacity"] == kitty["background_opacity"]
    assert ghostty["background-blur"] == kitty["background_blur"]
    assert files["ghostty/full.ghostty"].split("font-family = ")[1].strip('"\n') in files["kitty/full.conf"]


def test_the_readme_counts_every_app():
    readme = (paths.ROOT / "README.md").read_text(encoding="utf-8")
    badge = re.search(r"badge/apps-(\d+)-", readme)
    assert badge, "the apps badge is gone"
    assert int(badge[1]) == len(every())
