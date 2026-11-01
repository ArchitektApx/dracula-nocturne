"""What each screenshot shows: one Scene per app and level, assets/apps/<app>-<level>.png.

A scene runs a command in a scratch home themed at its level, or is a placeholder for apps whose
windows can't be captured from a terminal (those get real screenshots by hand).
"""

import hashlib
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from capture import Home
from frames import Frame

from nocturne import paths
from nocturne.app import Level

T, L, F = Level.THEME, Level.LOOK, Level.FULL
COLORS = (
    "for i in 0 1 2 3 4 5 6 7; do printf '\\033[4%sm   \\033[0m' $i; done; echo; "
    "for i in 0 1 2 3 4 5 6 7; do printf '\\033[10%sm   \\033[0m' $i; done; echo"
)


@dataclass(frozen=True)
class Scene:
    app: str
    level: Level
    frame: Frame
    command: Callable[[Home], str] | None = None  # None: a placeholder
    size: tuple[int, int] = (84, 16)
    keys: list[str] = field(default_factory=list)
    wait: float = 2.0
    needs: str = ""  # a program the scene can't do without
    after: tuple[str, ...] = ()  # a command that cleans up behind it

    @property
    def name(self) -> str:
        return f"{self.app}-{self.level}"


def shell(h: Home) -> str:
    """A plain prompt in the project, with the colours and a file listing."""
    return f"cd {h.project} && {COLORS} && PS1='$ ' sh"


def terminal(app: str, tabs: tuple[str, ...] = ()) -> list[Scene]:
    keys = ["eza -l --icons --no-user --git\tEnter"]
    return [
        Scene(app, T, Frame("window", title=app.title(), tabs=tabs), shell, (84, 12), keys),
        Scene(app, L, Frame("glass", tabs=tabs), shell, (84, 12), keys),
        Scene(app, F, Frame("glass", tabs=tabs), lambda h: f"tmux new -s demo '{h.zsh()}'", (84, 13),
              keys, wait=4.0),
    ]  # fmt: skip


BTOP = Path(__file__).parent / "btop"  # the container: btop, its config, and some load for it to show
CONTAINER = "nocturne-btop-shot"  # closing the pane leaves a container running: this one is removed after


def btop(_h: Home) -> str:
    """btop in a throwaway Linux container, so its processes and network are the container's.
    Only the theme comes in, from the checkout (Docker shares the home folder, not the scratch one)."""
    digest = hashlib.sha256(b"".join(f.read_bytes() for f in sorted(BTOP.iterdir()))).hexdigest()[:12]
    image = f"nocturne-btop:{digest}"
    if subprocess.run(["docker", "image", "inspect", image], capture_output=True, check=False).returncode:
        subprocess.run(["docker", "build", "-q", "-t", image, str(BTOP)], capture_output=True, check=True)
    inspect = ["docker", "context", "inspect", "--format", "{{.Endpoints.docker.Host}}"]
    host = subprocess.run(inspect, capture_output=True, text=True, check=True).stdout.strip()
    env = "-e LANG=C.UTF-8 -e TERM -e COLORTERM"
    return f"DOCKER_HOST={host} docker run --rm -it --name {CONTAINER} --hostname nocturne {env} -v {paths.THEMES / 'btop'}:/root/.config/btop/themes:ro {image}"


def nvim(h: Home) -> str:
    return f'cd {h.project} && nvim bat.py "+normal 13G16|"'


SCENES: list[Scene] = [
    *terminal("ghostty"),
    *terminal("kitty", tabs=("zsh", "nvim", "btop")),
    Scene("tmux", T, Frame("card"), lambda h: f"tmux new -s demo -n '~' '{h.zsh()}' \\; new-window -n nvim \\; select-window -t 0", (84, 8), wait=3.0),
    Scene("p10k", T, Frame("card"), lambda h: h.zsh(), (84, 6), ["git status -s\tEnter"], wait=3.0, needs="zsh"),
    Scene("p10k", F, Frame("card"), lambda h: h.zsh(), (84, 6), ["git status -s\tEnter"], wait=3.0, needs="zsh"),
    Scene("omp", T, Frame("card"), lambda h: f'cd {h.project} && pwsh -NoLogo -NoProfile -NoExit -Command "oh-my-posh init pwsh --config {h.root}/.config/dracula-nocturne/omp/dracula-nocturne.omp.json | Invoke-Expression"', (110, 3), wait=4.0, needs="pwsh"),
    Scene("nvim", T, Frame("glass", fill="editor.bg"), nvim, (84, 18), wait=2.5),
    Scene("nvim", F, Frame("glass"), lambda h: f"cd {h.project} && nvim", (100, 30), wait=5.0),
    Scene("bat", T, Frame("card"), lambda h: f"cd {h.project} && bat --style=numbers --color=always bat.py", (84, 16)),
    Scene("eza", T, Frame("card"), lambda h: f"cd {h.project} && eza -l --icons --git --no-user", (84, 8)),
    Scene("ls_colors", T, Frame("card"), lambda h: f". {h.root}/.config/dracula-nocturne/ls_colors/ls_colors.sh && cd {h.project} && (gls -go --color=always 2>/dev/null || ls -go --color=always)", (84, 8)),
    Scene("fzf", T, Frame("card"), lambda h: f". {h.root}/.config/dracula-nocturne/fzf/fzf.sh && cd {h.project} && find src -name '*.py' | fzf --height=100% --query=apps", (84, 10)),
    Scene("yazi", T, Frame("card"), lambda h: f"cd {h.project}/src/nocturne && yazi", (84, 16), wait=3.5),
    Scene("btop", T, Frame("card"), btop, (120, 32), wait=24.0, needs="docker", after=("docker", "rm", "-f", CONTAINER)),
    Scene("lazygit", T, Frame("card"), lambda h: f"cd {h.project} && lazygit", (110, 26), ["Enter"], wait=3.5),  # Enter: past its welcome
    Scene("iris", T, Frame("placeholder")),
    Scene("vscode", T, Frame("placeholder")),
    Scene("cursor", T, Frame("placeholder")),
    Scene("t3code", T, Frame("placeholder")),
    Scene("zen", F, Frame("placeholder")),
    Scene("borders", T, Frame("placeholder")),
]  # fmt: skip
