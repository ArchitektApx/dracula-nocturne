"""What install changed that undo needs to know about, kept in $XDG_STATE_HOME/dracula-nocturne/state.json.

- created: files and folders install had to create, removed again by undo once they're empty
- copies: files install wrote as copies, with a hash, so undo only removes them while unchanged
- lines: include lines install added, by app, so they come out even after their text changed
- own: folders made just to hold the state file, removed with it
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import cast

from nocturne import paths, system

UTF8 = "utf-8"


def missing_parents(path: Path) -> list[Path]:
    """path and its parents that don't exist yet, outermost first."""
    return [p for p in reversed((path, *path.parents)) if not p.exists() and not p.is_symlink()]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def empty(path: Path) -> bool:
    """An empty folder, or a file with nothing but whitespace (never a link)."""
    if path.is_symlink():
        return False
    if path.is_dir():
        return not any(path.iterdir())
    return path.is_file() and not path.read_text(encoding=UTF8, errors="replace").strip()


class Ledger:
    def __init__(self, file: Path | None = None) -> None:
        self.file = file or system.state_home() / paths.NAME / "state.json"
        data: dict[str, object] = {}
        if self.file.is_file():
            data = cast("dict[str, object]", json.loads(self.file.read_text(encoding=UTF8)))
        self.created = cast("list[str]", data.get("created", []))
        self.copies = cast("dict[str, str]", data.get("copies", {}))
        self.lines = cast("list[list[str]]", data.get("lines", []))  # [app, file, text]
        self.own = cast("list[str]", data.get("own", []))

    def mkdirs(self, folder: Path) -> None:
        """mkdir -p, remembering every folder that wasn't there."""
        new = missing_parents(folder)
        folder.mkdir(parents=True, exist_ok=True)
        self.add_created(*new)

    def add_created(self, *created: Path) -> None:
        self.created += [str(p) for p in created if str(p) not in self.created]
        self.save()

    def record_copy(self, dest: Path) -> None:
        self.copies[str(dest)] = sha(dest)
        self.save()

    def forget_copy(self, dest: Path) -> None:
        self.copies.pop(str(dest), None)
        self.save()

    def record_line(self, app: str, file: Path, text: str) -> None:
        if [app, str(file), text] not in self.lines:
            self.lines.append([app, str(file), text])
            self.save()

    def forget_line(self, file: Path, text: str) -> None:
        self.lines = [entry for entry in self.lines if entry[1:] != [str(file), text]]
        self.save()

    def lines_of(self, app: str) -> list[tuple[str, str]]:
        return [(file, text) for owner, file, text in self.lines if owner == app]

    def our_copy(self, dest: Path) -> bool:
        """A copy install wrote that nobody has changed since."""
        recorded = self.copies.get(str(dest))
        return recorded is not None and dest.is_file() and not dest.is_symlink() and sha(dest) == recorded

    def tidy(self) -> list[Path]:
        """Remove the files and folders install created that are empty now; returns them."""
        removed: list[Path] = []
        keep: list[str] = []
        last: list[str] = []  # folders that hold nothing but this ledger (on Windows: AppData)
        for entry in sorted(self.created, key=lambda p: len(Path(p).parts), reverse=True):  # deepest first
            path = Path(entry)
            if empty(path):
                path.rmdir() if path.is_dir() else path.unlink()
                removed.append(path)
            elif self.only_ledger(path):
                last.append(entry)
            elif path.exists() or path.is_symlink():
                keep.append(entry)
        if keep or self.copies or self.lines:  # the ledger stays, and so do the folders around it
            keep, last = keep + last, []
        self.created = keep
        self.save()  # without anything to remember, this takes the ledger and its folders away
        for path in map(Path, last):
            if empty(path):
                path.rmdir()
                removed.append(path)
        return removed

    def only_ledger(self, path: Path) -> bool:
        """A folder with nothing in it but this ledger's file and the folders made for it."""
        if not path.is_dir() or path.is_symlink():
            return False
        mine = {self.file, *map(Path, self.own)}
        return all(p in mine and (p == self.file or self.only_ledger(p)) for p in path.iterdir())

    def save(self) -> None:
        if self.created or self.copies or self.lines:
            if not self.file.parent.exists():
                self.own = [str(p) for p in missing_parents(self.file.parent)]
                self.file.parent.mkdir(parents=True)
            data = {"created": self.created, "copies": self.copies, "lines": self.lines, "own": self.own}
            self.file.write_text(json.dumps(data, indent=2) + "\n", encoding=UTF8)
            return
        self.file.unlink(missing_ok=True)
        for folder in map(Path, reversed(self.own)):  # deepest first
            if folder.is_dir() and not any(folder.iterdir()):
                folder.rmdir()
        self.own = []
