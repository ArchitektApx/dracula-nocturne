"""Theme files put where an app looks for them: as a link into the checkout, or as a copy.

A file of the user's that's in the way is left alone, or with --force moved aside to
NAME.before-nocturne, which undo puts back.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

from nocturne import paths, system
from nocturne.steps.base import Context, Outcome, Step
from nocturne.style import DIM, GREEN, PINK, RESET, YELLOW, say

if TYPE_CHECKING:
    from pathlib import Path

BACKUP = ".before-nocturne"
UTF8 = "utf-8"


def there(path: Path) -> bool:
    """Exists, counting a link whose target is gone."""
    return path.exists() or path.is_symlink()


def is_link(path: Path) -> bool:
    return path.is_symlink() or os.path.isjunction(path)


def link_target(path: Path) -> Path:
    """Where a link points, through any links in the folders on the way. Read rather than resolved:
    Windows can't resolve a link whose target is gone (a renamed theme, a moved checkout)."""
    target = path.parent / str(path.readlink()).removeprefix("\\\\?\\")  # an absolute one replaces the folder
    return target.parent.resolve() / target.name


def into_themes(path: Path) -> bool:
    """A link that ends up in this checkout's themes/."""
    if not is_link(path):
        return False
    target, themes = link_target(path), paths.THEMES.resolve()
    return target == themes or themes in target.parents


def remove_link(path: Path) -> None:
    os.rmdir(path) if os.path.isjunction(path) else path.unlink()  # noqa: PTH106  # a junction is removed like a folder


@dataclass(frozen=True)
class Copy(Step):
    """A copy of a theme file, for apps that won't read a link (T3 Code). Install refreshes it."""

    src: str  # relative to themes/
    dest: Path

    @property
    def backup(self) -> Path:
        return self.dest.with_name(self.dest.name + BACKUP)

    def placed(self, ctx: Context) -> bool:  # noqa: ARG002
        source = paths.THEMES / self.src
        return self.dest.is_file() and not is_link(self.dest) and self.dest.read_bytes() == source.read_bytes()

    def ours(self, ctx: Context) -> bool:
        return ctx.ledger.our_copy(self.dest)

    def put(self, ctx: Context) -> None:
        """Write through a temporary file and a rename, so the app never reads half of it."""
        ctx.ledger.mkdirs(self.dest.parent)
        tmp = self.dest.with_name(f".{self.dest.name}.nocturne-tmp")
        tmp.write_bytes((paths.THEMES / self.src).read_bytes())
        tmp.replace(self.dest)
        ctx.ledger.record_copy(self.dest)

    def added(self) -> str:
        return f"{system.display(self.dest)} {DIM}(a copy: run install again after a build){RESET}"

    def apply(self, ctx: Context) -> Outcome:
        if self.placed(ctx):
            say("=", DIM, f"{system.display(self.dest)} {DIM}already in place{RESET}")
            return Outcome.DONE
        if there(self.dest) and not self.ours(ctx) and not self._move_aside(ctx):
            return Outcome.BLOCKED
        say("+", GREEN, self.added())
        if not ctx.dry_run:
            self.put(ctx)
        return Outcome.DONE

    def _move_aside(self, ctx: Context) -> bool:
        name = system.display(self.dest)
        if not ctx.force:
            say("!", YELLOW, f"{name} is in the way, left alone {DIM}(--force moves it to {self.backup.name}){RESET}")
            return False
        if there(self.backup):
            say("!", YELLOW, f"{name} and {self.backup.name} are both there, left alone: move one of them first")
            return False
        say("~", YELLOW, f"{name} -> {self.backup.name}")
        if not ctx.dry_run:
            self.dest.rename(self.backup)
        return True

    def remove(self, ctx: Context) -> bool:
        """Remove what install put there; False if it isn't ours (any more)."""
        if not self.ours(ctx):
            if str(self.dest) in ctx.ledger.copies and there(self.dest):
                say("!", YELLOW, f"{system.display(self.dest)} changed since install, left alone")
            return False
        say("-", PINK, system.display(self.dest))
        if not ctx.dry_run:
            self.dest.unlink()
            ctx.ledger.forget_copy(self.dest)
        return True

    def undo(self, ctx: Context) -> None:
        removed = self.remove(ctx)
        if there(self.backup) and (not there(self.dest) or (ctx.dry_run and removed)):
            say("~", YELLOW, f"{self.backup.name} -> {system.display(self.dest)}")
            if not ctx.dry_run:
                self.backup.rename(self.dest)
        if not ctx.dry_run and not there(self.dest):
            ctx.ledger.forget_copy(self.dest)

    def check(self, ctx: Context) -> bool:
        return self.placed(ctx)

    def stale(self, ctx: Context) -> bool:
        return ctx.ledger.our_copy(self.dest) and not self.placed(ctx)


@dataclass(frozen=True)
class Link(Copy):
    """A link to a theme file or folder, through paths.link_dir(), so a build reaches it at once.
    Where the system won't make one (Windows without Developer Mode) a folder becomes a junction
    and a file a copy."""

    # link straight to themes/src rather than through link_dir() (for link_dir() itself)
    direct: bool = False

    @property
    def target(self) -> Path:
        return paths.THEMES / self.src if self.direct else paths.theme(self.src)

    def placed(self, ctx: Context) -> bool:
        if is_link(self.dest):
            return self.dest.resolve() == self.target.resolve()
        return str(self.dest) in ctx.ledger.copies and super().placed(ctx)

    def ours(self, ctx: Context) -> bool:
        # link_dir() itself, left dangling by a checkout that moved, is ours to replace
        dangling_root = self.direct and is_link(self.dest) and not self.dest.exists()
        return into_themes(self.dest) or dangling_root or super().ours(ctx)

    def added(self) -> str:
        return f"{system.display(self.dest)} -> {system.display(self.target)}"

    def put(self, ctx: Context) -> None:
        ctx.ledger.mkdirs(self.dest.parent)
        if is_link(self.dest):  # one of ours that points somewhere else (a renamed theme, a moved checkout)
            remove_link(self.dest)
        folder = (paths.THEMES / self.src).is_dir()
        try:
            self.dest.symlink_to(self.target, target_is_directory=folder)
        except OSError:
            if system.current() is not system.OS.WINDOWS:
                raise
            if folder:
                import _winapi  # noqa: PLC0415  # pyright: ignore[reportMissingModuleSource]  # Windows only

                _winapi.CreateJunction(str(self.target.resolve()), str(self.dest))  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
            else:
                say("~", YELLOW, f"{system.display(self.dest)} {DIM}is a copy: links need Developer Mode{RESET}")
                super().put(ctx)

    def remove(self, ctx: Context) -> bool:
        if not self.ours(ctx) or not is_link(self.dest):
            return super().remove(ctx)
        say("-", PINK, system.display(self.dest))
        if not ctx.dry_run:
            remove_link(self.dest)
        return True


@dataclass(frozen=True)
class Touch(Step):
    """An empty file where an app won't start without one (lazygit and the files in LG_CONFIG_FILE).
    One that's there is left alone; undo's tidy-up takes ours away while it's still empty."""

    dest: Path

    def apply(self, ctx: Context) -> Outcome:
        if there(self.dest):
            return Outcome.DONE
        say("+", GREEN, f"{system.display(self.dest)} {DIM}(empty, for you to fill){RESET}")
        if not ctx.dry_run:
            ctx.ledger.mkdirs(self.dest.parent)
            self.dest.touch()
            ctx.ledger.add_created(self.dest)
        return Outcome.DONE

    def check(self, ctx: Context) -> bool | None:  # noqa: ARG002
        return there(self.dest)
