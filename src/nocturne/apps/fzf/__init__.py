"""fzf: colours put in front of FZF_DEFAULT_OPTS, so anything the user sets still wins."""

from __future__ import annotations

from typing import TYPE_CHECKING

from nocturne import shells, system
from nocturne.app import App, Group, Level, Tier
from nocturne.template import header

if TYPE_CHECKING:
    from nocturne.palette import Palette

NOTE = "# Goes in front of your own FZF_DEFAULT_OPTS, so anything you set yourself wins.\n"
COLORS = {
    "fg": "fg", "hl": "purple", "fg+": "fg", "bg+": "selection", "hl+": "pink",
    "info": "comment", "prompt": "green", "pointer": "pink", "marker": "pink", "spinner": "orange",
    "header": "comment", "border": "comment", "label": "purple", "query": "fg",
}  # fmt: skip
# prompt, pointer and marker
GLYPHS = ("❯", "▌", "┃")  # noqa: RUF001


def options(p: Palette, prompt: str, pointer: str, marker: str) -> str:
    colors = ",".join(f"{k}:{p[v].hex}" for k, v in COLORS.items())
    glyphs = f"--prompt='{prompt} ' --pointer='{pointer}' --marker='{marker}'"
    return f"--color={colors},bg:-1,gutter:-1 --border=rounded {glyphs}"


def generate(p: Palette) -> dict[str, str]:
    opts = options(p, *GLYPHS)
    # Windows PowerShell reads scripts without a BOM as ANSI, so the glyphs are written as code points there
    ps_opts = options(p, *(f"$([char]0x{ord(g):04X})" for g in GLYPHS))
    return {
        "fzf.sh": header(p, "fzf (bash, zsh)")
        + NOTE
        + f'_nocturne_fzf="{opts}"\n'
        + 'case "$FZF_DEFAULT_OPTS" in\n'
        + '  *"$_nocturne_fzf"*) ;;  # already there (a nested shell, or sourced twice)\n'
        + '  *) export FZF_DEFAULT_OPTS="$_nocturne_fzf${FZF_DEFAULT_OPTS:+ $FZF_DEFAULT_OPTS}" ;;\n'
        + "esac\nunset _nocturne_fzf\n",
        "fzf.fish": header(p, "fzf (fish)")
        + NOTE
        + f'set -l opts "{opts}"\n'
        + 'if not string match -q -- "*$opts*" "$FZF_DEFAULT_OPTS"\n'
        + '    set -gx FZF_DEFAULT_OPTS (string trim -- "$opts $FZF_DEFAULT_OPTS")\n'
        + "end\n",
        "fzf.ps1": header(p, "fzf (PowerShell)")
        + NOTE
        + f'$opts = "{ps_opts}"\n'
        + 'if (-not "$env:FZF_DEFAULT_OPTS".Contains($opts)) {\n'
        + '    $env:FZF_DEFAULT_OPTS = "$opts $env:FZF_DEFAULT_OPTS".Trim()\n'
        + "}\nRemove-Variable opts\n",
    }


APP = App(
    id="fzf",
    title="fzf",
    url="https://github.com/junegunn/fzf",
    group=Group.TOOL,
    binary="fzf",
    platforms=system.EVERYWHERE,
    generate=generate,
    tiers={
        Level.THEME: Tier(
            "colours, a rounded border and prompt; your own options still win", lambda: shells.sourced("fzf/fzf")
        )
    },
)
