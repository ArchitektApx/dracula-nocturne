"""The theme as a VS Code extension, for VS Code and Cursor alike: themes/vscode packed into a
.vsix (a zip, no Node needed) and installed with the editor's own command line."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from nocturne import paths, system
from nocturne.app import Level, Tier
from nocturne.steps import Note, Outcome, Run, Step

if TYPE_CHECKING:
    from nocturne.steps import Context

PUBLISHER, NAME = "ArchitektApx", "dracula-nocturne"
EXTENSION_ID = f"{PUBLISHER}.{NAME}".lower()


def vsix(dest: Path) -> Path:
    """themes/vscode packed as an extension: everything goes under extension/ in the zip."""
    source = paths.THEMES / "vscode"
    out = dest / f"{NAME}.vsix"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(source.rglob("*")):
            if f.is_file():
                zf.write(f, f"extension/{f.relative_to(source).as_posix()}")
    return out


def cli(name: str, bundle: str) -> str | None:
    """The editor's command line: on PATH, or inside the macOS app."""
    if found := shutil.which(name):
        return found
    app = system.bundle(bundle)
    inside = app / "Contents" / "Resources" / "app" / "bin" / name if app else None
    return str(inside) if inside and inside.exists() else None


@dataclass(frozen=True)
class Extension(Step):
    """The theme as an extension, installed (again, after a build) with the editor's command line."""

    name: str  # the command: code, cursor
    bundle: str

    def _installed(self, binary: str) -> bool:
        try:
            done = subprocess.run(
                [binary, "--list-extensions"], capture_output=True, text=True, check=False, timeout=30
            )
        except (OSError, subprocess.TimeoutExpired):
            return False
        return EXTENSION_ID in done.stdout.lower().split()

    def apply(self, ctx: Context) -> Outcome:
        binary = cli(self.name, self.bundle) or self.name
        with tempfile.TemporaryDirectory() as tmp:
            why = "the theme as an extension, packed from themes/vscode"
            return Run((binary, "--install-extension", str(vsix(Path(tmp))), "--force"), why).apply(ctx)

    def undo(self, ctx: Context) -> None:
        binary = cli(self.name, self.bundle)
        if binary and self._installed(binary):
            Run((binary, "--uninstall-extension", EXTENSION_ID), "remove the extension").apply(ctx)

    def check(self, ctx: Context) -> bool | None:  # noqa: ARG002
        binary = cli(self.name, self.bundle)
        return self._installed(binary) if binary else None


def tiers(name: str, bundle: str) -> dict[Level, Tier]:
    select = Note(
        'Select it: "Preferences: Color Theme" > Dracula Nocturne, or "workbench.colorTheme": "Dracula Nocturne"'
    )
    return {
        Level.THEME: Tier(
            "window chrome on near-black, Pierre Dark's code colours", lambda: [Extension(name, bundle), select]
        )
    }
