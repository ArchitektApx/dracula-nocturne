"""Run apps in a private tmux server against a scratch home folder themed by `nocturne install`, and
capture their panes. Nothing of the user's is read or changed: HOME and the XDG folders point at
the scratch folder."""

import glob
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from nocturne import paths
from nocturne.app import Level

# Where package and plugin managers put Powerlevel10k; P10K_DIR wins
P10K = [
    "/opt/homebrew/share/powerlevel10k", "/usr/share/zsh-theme-powerlevel10k", "~/powerlevel10k",
    "~/.oh-my-zsh/custom/themes/powerlevel10k", "~/.local/share/zinit/plugins/romkatv---powerlevel10k",
    "~/Library/Caches/antidote/*powerlevel10k", "~/.cache/antidote/*powerlevel10k",
]  # fmt: skip
SAMPLE = '''from dataclasses import dataclass

MAX_HEIGHT = 120  # metres


@dataclass
class Bat:
    """A small one."""

    name: str = "Nocturne\\n"
    wings: int = 2

    def fly(self, height: float) -> bool:
        return 0 < height <= MAX_HEIGHT and self.wings == 2
'''
# Apps the scratch homes are themed for (the GUI ones get no capture)
APPS = ["tmux", "p10k", "nvim", "bat", "yazi", "lazygit", "eza", "ls_colors", "fzf", "iris"]


def p10k_dir() -> Path | None:
    candidates = [os.environ.get("P10K_DIR", ""), *P10K]
    found = (Path(m) for c in candidates if c for m in glob.glob(os.path.expanduser(c)))
    return next((d for d in found if (d / "powerlevel10k.zsh-theme").exists()), None)


@dataclass
class Home:
    """A scratch home folder, themed at one level."""

    root: Path
    level: Level

    @property
    def project(self) -> Path:
        return self.root / "dracula-nocturne"

    def env(self) -> dict[str, str]:
        keep = {k: v for k, v in os.environ.items() if k in {"PATH", "LANG", "LC_ALL", "USER", "TMPDIR"}}
        r = self.root
        return {
            **keep,
            "HOME": str(r),
            "XDG_CONFIG_HOME": str(r / ".config"),
            "XDG_DATA_HOME": str(r / ".local" / "share"),
            "XDG_STATE_HOME": str(r / ".local" / "state"),
            "XDG_CACHE_HOME": str(r / ".cache"),
            "TERM": "xterm-256color",
            "COLORTERM": "truecolor",
            "GIT_AUTHOR_NAME": "Nocturne",
            "GIT_AUTHOR_EMAIL": "bat@example.org",
            "GIT_COMMITTER_NAME": "Nocturne",
            "GIT_COMMITTER_EMAIL": "bat@example.org",
        }

    def run(self, *argv: str | Path) -> None:
        subprocess.run([str(a) for a in argv], env=self.env(), cwd=self.root, capture_output=True, check=False)

    def prepare(self) -> None:
        """A small git project, a .zshrc that loads p10k, then `nocturne install` at the level."""
        shutil.copytree(paths.ROOT / "src", self.project / "src", ignore=shutil.ignore_patterns("__pycache__"))
        for name in ("palette.toml", "README.md", "LICENSE", "pyproject.toml"):
            shutil.copy(paths.ROOT / name, self.project)
        (self.project / "bat.py").write_text(SAMPLE, encoding="utf-8")
        # a script and a link, so file listings show more than one kind of file
        (self.project / "build.sh").write_text("#!/bin/sh\nuv run nocturne build\n", encoding="utf-8")
        (self.project / "build.sh").chmod(0o755)
        (self.project / "colors.toml").symlink_to("palette.toml")
        for argv in (["init", "-q", "-b", "main"], ["add", "."], ["commit", "-qm", "first"]):
            self.run("git", "-C", self.project, *argv)
        palette = self.project / "palette.toml"  # a small change, for the prompt's and lazygit's git status
        palette.write_text(
            palette.read_text(encoding="utf-8").replace("Dracula Nocturne", "Dracula Nocturne, later"), encoding="utf-8"
        )
        p10k = p10k_dir()
        zshrc = ["export LANG=en_US.UTF-8"]
        if p10k:
            zshrc += [f"source {p10k}/powerlevel10k.zsh-theme", "[[ -f ~/.p10k.zsh ]] && source ~/.p10k.zsh"]
            if self.level < Level.FULL:  # a stock config of the user's own, for the overlay to go over
                shutil.copy(p10k / "config" / "p10k-lean.zsh", self.root / ".p10k.zsh")
        (self.root / ".zshrc").write_text("\n".join(zshrc) + "\n", encoding="utf-8")
        nvim = self.root / ".config" / "nvim"
        nvim.mkdir(parents=True)
        if self.level < Level.FULL:
            (nvim / "init.lua").write_text(
                'vim.o.number = true\nvim.o.cursorline = true\nvim.o.shortmess = vim.o.shortmess .. "I"\n'
                'vim.cmd.colorscheme("dracula-nocturne")\n',
                encoding="utf-8",
            )
        level = str(self.level)
        self.run(sys.executable, "-m", "nocturne", "install", "-y", "--level", level, *APPS)
        if p10k:  # a first start, while p10k fetches its git helper
            capture(self, self.zsh(), (80, 10), [], wait=8)
        if self.level is Level.FULL and shutil.which("nvim"):
            self.run("nvim", "--headless", "+Lazy! sync", "+qa")  # LazyVim's plugins, from GitHub
            # a first start in a real pane, long enough for the parsers LazyVim installs in the background
            capture(self, f"cd {self.project} && nvim", (100, 30), [], wait=90)

    def zsh(self) -> str:
        return f"cd {self.project} && ZDOTDIR={self.root} zsh -i"


def home(base: Path, level: Level) -> Home:
    h = Home(base / str(level), level)
    h.root.mkdir(parents=True)
    h.prepare()
    return h


def scratch() -> Path:
    return Path(tempfile.mkdtemp(prefix="nocturne-shots-"))


@dataclass
class Pane:
    text: str  # with ANSI colours
    cursor: tuple[int, int]  # column, row


def capture(home: Home, command: str, size: tuple[int, int], keys: list[str], wait: float) -> Pane:
    """command in a fresh pane of size (columns, rows); keys typed after wait/2, captured after wait."""
    server = ["tmux", "-L", f"nocturne-shots-{os.getpid()}", "-f", os.devnull]
    inner = tempfile.mkdtemp(prefix="tmux-")  # a tmux started in the pane gets a server of its own here
    env = [f"{k}={v}" for k, v in {**home.env(), "TMUX_TMPDIR": inner}.items()]
    start = [*server, "new-session", "-d", "-x", str(size[0]), "-y", str(size[1])]
    subprocess.run([*start, "env", "-i", *env, "sh", "-c", f"{command}; sleep 60"], check=True, cwd=home.root)
    try:
        time.sleep(wait / 2)
        for key in keys:
            subprocess.run([*server, "send-keys", *key.split("\t")], check=True)
            time.sleep(0.4)
        time.sleep(wait / 2)
        text = subprocess.run([*server, "capture-pane", "-pe", "-N"], capture_output=True, text=True, check=True).stdout
        where = subprocess.run(
            [*server, "display", "-p", "#{cursor_x} #{cursor_y}"], capture_output=True, text=True, check=True
        )
        x, y = map(int, where.stdout.split())
        return Pane(text, (x, y))
    finally:
        subprocess.run([*server, "kill-server"], capture_output=True, check=False)
        subprocess.run(
            ["tmux", "kill-server"], env={**os.environ, "TMUX_TMPDIR": inner}, capture_output=True, check=False
        )
        shutil.rmtree(inner, ignore_errors=True)
