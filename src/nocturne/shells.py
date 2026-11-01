"""Hooking a theme into the user's shells: zsh, bash, fish and PowerShell.

On macOS and Linux only rc files that are already there get a line, so a zsh user doesn't end up
with a .bashrc. On Windows, where PowerShell is the shell, its profile is created if need be.
"""

from __future__ import annotations

import shutil
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

from nocturne import paths, system
from nocturne.steps import Line, Link

if TYPE_CHECKING:
    from nocturne.steps import Step

WINDOWS = system.OS.WINDOWS


def zshrc() -> Path:
    return (system.env_dir("ZDOTDIR") or system.home()) / ".zshrc"


def bashrcs() -> tuple[Path, Path]:
    return system.home() / ".bashrc", system.home() / ".bash_profile"


def bashrc() -> Path:
    """~/.bashrc; on macOS, where Terminal starts login shells, ~/.bash_profile if that's the one there."""
    rc, profile = bashrcs()
    return profile if system.current() is system.OS.MACOS and profile.exists() and not rc.exists() else rc


def fish_used() -> bool:
    return bool(shutil.which("fish")) or (system.config_home() / "fish").is_dir()


def fish_conf(name: str) -> Path:
    return system.config_home() / "fish" / "conf.d" / f"{paths.NAME}-{name}.fish"


@cache
def _profile(shell: str) -> Path | None:
    """A PowerShell's own answer to $PROFILE (it follows a moved Documents folder), if it's installed."""
    found = system.ask([shell, "-NoLogo", "-NoProfile", "-Command", "$PROFILE.CurrentUserCurrentHost"])
    return Path(found) if found else None


def pwsh_profiles() -> list[Path]:
    """The profiles of the PowerShells that are installed: PowerShell 7 everywhere, and Windows PowerShell."""
    shells = ["pwsh", "powershell"] if system.current() is WINDOWS else ["pwsh"]
    return [p for p in map(_profile, shells) if p]


def var(path: Path, *, posix: bool = False) -> str:
    """path for a shell line, with the home folder as $HOME (zsh, bash, fish and PowerShell all know
    it). On Windows the AppData folders are named by their own variables, which PowerShell agrees
    on even where $HOME is somewhere else (a network drive); posix: as Git Bash and co. name them."""
    bases = [("$HOME", system.home())]
    if system.current() is WINDOWS:
        env = "$" if posix else "$env:"
        bases = [(f"{env}APPDATA", system.appdata()), (f"{env}LOCALAPPDATA", system.local_appdata()), *bases]
    for name, base in bases:
        if path.is_relative_to(base):
            return f"{name}/{path.relative_to(base).as_posix()}"
    return path.as_posix()


def _posix_rcs() -> list[tuple[Path, tuple[Path, ...]]]:
    return [(zshrc(), ()), (bashrc(), bashrcs())]


def sourced(stem: str) -> list[Step]:
    """Load themes/<stem>.sh, .fish and .ps1 (whichever exist) in every shell the user has."""
    steps: list[Step] = []
    sh, fish, ps1 = (paths.THEMES / f"{stem}{ext}" for ext in (".sh", ".fish", ".ps1"))
    if sh.exists() and system.current() is not WINDOWS:
        f = var(paths.theme(f"{stem}.sh"))
        steps += [Line(rc, f'[ -r "{f}" ] && . "{f}"', only_existing=True, also=also) for rc, also in _posix_rcs()]
    if fish.exists() and system.current() is not WINDOWS and fish_used():
        steps.append(Link(f"{stem}.fish", fish_conf(stem.split("/", maxsplit=1)[0])))
    if ps1.exists():
        f = var(paths.theme(f"{stem}.ps1"))
        line = f'if (Test-Path "{f}") {{ . "{f}" }}'
        steps += [Line(p, line, only_existing=system.current() is not WINDOWS) for p in pwsh_profiles()]
    return steps


def exported(name: str, value: str) -> list[Step]:
    """Set an environment variable in every shell the user has. value may use $HOME."""
    steps: list[Step] = []
    if system.current() is not WINDOWS:
        steps += [Line(rc, f'export {name}="{value}"', only_existing=True, also=also) for rc, also in _posix_rcs()]
        if fish_used():
            steps.append(Line(fish_conf(name.lower()), f'set -gx {name} "{value}"'))
    line = f'$env:{name} = "{value}"'
    steps += [Line(p, line, only_existing=system.current() is not WINDOWS) for p in pwsh_profiles()]
    return steps
