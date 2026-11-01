"""oh-my-posh: a whole prompt config (oh-my-posh themes are complete configs), with the p10k tiles."""

from __future__ import annotations

from nocturne import paths, shells, system
from nocturne.app import App, Group, Level, Tier
from nocturne.steps import Note


def note() -> Note:
    theme = paths.theme("omp/dracula-nocturne.omp.json")
    config, posix = shells.var(theme), shells.var(theme, posix=True)
    return Note(
        "Start oh-my-posh with it in your shell's profile, in place of your current init line:\n"
        f'      PowerShell:  oh-my-posh init pwsh --config "{config}" | Invoke-Expression\n'
        f'      zsh, bash:   eval "$(oh-my-posh init zsh --config "{posix}")"\n'
        f'      fish:        oh-my-posh init fish --config "{posix}" | source'
    )


APP = App(
    id="omp",
    title="oh-my-posh",
    url="https://ohmyposh.dev",
    group=Group.SHELL,
    binary="oh-my-posh",
    platforms=system.EVERYWHERE,
    tiers={Level.THEME: Tier("a complete prompt with rounded tiles, for any shell", lambda: [note()])},
)
