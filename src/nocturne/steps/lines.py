"""One include line added to a config file, under a marker comment. Undo removes the marker
together with the line, and only while that line is still exactly what install wrote.

The ledger remembers each line with its app, so a line that's no longer wanted (its path changed
with XDG_CONFIG_HOME, say) comes out on the next install or undo even though no step names it.
"""

from __future__ import annotations

import codecs
from dataclasses import dataclass, field
from pathlib import Path

from nocturne import system
from nocturne.steps.base import Context, Outcome, Step
from nocturne.style import DIM, GREEN, PINK, RESET, say

MARKER = "dracula-nocturne (remove with: nocturne install --undo)"
BOMS = [(codecs.BOM_UTF8, "utf-8-sig"), (codecs.BOM_UTF16_LE, "utf-16"), (codecs.BOM_UTF16_BE, "utf-16")]


def _encoding(file: Path) -> str:
    """The file's own encoding as far as a BOM tells (Windows PowerShell writes UTF-16), else UTF-8."""
    head = file.read_bytes()[:3] if file.is_file() else b""
    return next((name for bom, name in BOMS if head.startswith(bom)), "utf-8")


def read(file: Path) -> str:
    """The file's text as it is: bytes that aren't UTF-8 and CRLF line ends survive a read and write."""
    if not file.is_file():
        return ""
    with file.open(encoding=_encoding(file), errors="surrogateescape", newline="") as f:
        return f.read()


def write(file: Path, text: str) -> None:
    file.write_text(text, encoding=_encoding(file), errors="surrogateescape", newline="")


def newline(text: str) -> str:
    """The line end a file uses (Windows editors write CRLF), so added lines match it."""
    return "\r\n" if "\r\n" in text else "\n"


@dataclass(frozen=True)
class Line(Step):
    file: Path
    text: str
    # only if the file is there already (shell rc files: don't create a .bashrc for a zsh user)
    only_existing: bool = False
    # other files the line may have gone into, when the choice of file can change (tmux, Ghostty)
    also: tuple[Path, ...] = field(default=())
    comment: str = "#"

    @property
    def marker(self) -> str:
        return f"{self.comment} {MARKER}"

    def files(self) -> list[Path]:
        return [self.file, *(f for f in self.also if f != self.file)]

    def apply(self, ctx: Context) -> Outcome:
        if self.only_existing and not self.file.exists():
            return Outcome.SKIPPED
        name = system.display(self.file)
        content = read(self.file)
        if self.text in content.splitlines():
            say("=", DIM, f"{name} {DIM}already has: {self.text}{RESET}")
            if not ctx.dry_run:
                ctx.ledger.record_line(ctx.app, self.file, self.text)
            return Outcome.DONE
        say("+", GREEN, f"{name}: {self.text}")
        if ctx.dry_run:
            return Outcome.DONE
        if not self.file.exists():
            ctx.ledger.mkdirs(self.file.parent)
            ctx.ledger.add_created(self.file)
        nl = newline(content)
        if content:
            content += nl if content.endswith("\n") else nl * 2
        write(self.file, f"{content}{self.marker}{nl}{self.text}{nl}")
        ctx.ledger.record_line(ctx.app, self.file, self.text)
        return Outcome.DONE

    def undo(self, ctx: Context) -> None:
        for file in self.files():
            remove(ctx, file, self.text, self.marker)

    def check(self, ctx: Context) -> bool | None:  # noqa: ARG002
        existing = [f for f in self.files() if f.is_file()]
        if self.only_existing and not existing:
            return None
        return any(self.text in read(f).splitlines() for f in existing)

    @staticmethod
    def forget_others(ctx: Context, keep: list[Line]) -> None:
        """Take out the lines the app's install wrote earlier that none of `keep` stands for."""
        wanted = {(str(line.file), line.text) for line in keep}
        for file, text in ctx.ledger.lines_of(ctx.app):
            if (file, text) not in wanted:
                remove(ctx, Path(file), text)


def remove(ctx: Context, file: Path, text: str, marker: str | None = None) -> None:
    """Remove the marker and the line under it (any marker comment style, unless one is given)."""
    lines = read(file).splitlines(keepends=True)
    for i, line in enumerate(lines[:-1]):
        found = line.rstrip("\r\n")
        if (found == marker if marker else found.endswith(f" {MARKER}")) and lines[i + 1].rstrip("\r\n") == text:
            start = i - 1 if i and not lines[i - 1].strip() else i  # with the blank line install added
            say("-", PINK, f"{system.display(file)}: {text}")
            if not ctx.dry_run:
                write(file, "".join(lines[:start] + lines[i + 2 :]))
                ctx.ledger.forget_line(file, text)
            return
    if not ctx.dry_run:
        ctx.ledger.forget_line(file, text)
