"""Install, undo and doctor: run the steps of each app at the chosen level."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from nocturne import paths, system
from nocturne.app import Level
from nocturne.ledger import Ledger
from nocturne.steps import Context, Line, Link, Outcome
from nocturne.style import DIM, PINK, RESET, YELLOW, heading, say

if TYPE_CHECKING:
    from nocturne.app import App


@dataclass(frozen=True)
class Options:
    dry_run: bool = False
    force: bool = False
    level: Level = Level.LOOK


def _root() -> Link:
    return Link("", paths.link_dir(), direct=True)


def _context(opt: Options) -> Context:
    return Context(Ledger(), dry_run=opt.dry_run, force=opt.force)


def _done(opt: Options) -> None:
    if opt.dry_run:
        print(f"\n{DIM}dry run: nothing changed{RESET}")


def install(apps: list[App], opt: Options, named: bool = False) -> int:
    """Install the apps; unless they were named, skip those that aren't installed."""
    ctx = _context(opt)
    heading("themes")
    if _root().apply(ctx) is Outcome.BLOCKED:
        return 1
    blocked = 0
    for app in apps:
        level = app.level(opt.level)
        heading(f"{app.title} {DIM}{level or ''}{RESET}")
        if not app.supported():
            say("-", DIM, "not on this system")
        elif not named and not app.present():
            say("-", DIM, f"not found, skipped {DIM}(nocturne install {app.id} does it anyway){RESET}")
        else:
            try:
                blocked += _install(app, level, ctx)
            except (OSError, ValueError) as e:  # one app's trouble (an unreadable config) doesn't stop the rest
                say("!", YELLOW, f"{e}, skipped")
                blocked += 1
    _done(opt)
    return 1 if blocked else 0


def _install(app: App, level: Level | None, ctx: Context) -> int:
    """One app at a level; returns how many steps something was in the way of."""
    ctx.app = app.id
    for step in app.undo_steps(above=level):  # a lower level than last time: the rest comes out
        step.undo(ctx)
    if level is None:
        say("-", DIM, f"starts at --level {min(app.tiers)}")
        return 0
    steps = app.steps(level)
    outcomes = [step.apply(ctx) for step in steps]
    Line.forget_others(ctx, [s for s in steps if isinstance(s, Line)])
    if all(o is Outcome.SKIPPED for o in outcomes) and not any(s.manual for s in steps):
        say("!", YELLOW, "nothing to hook into: none of its config files are there")
    return outcomes.count(Outcome.BLOCKED)


def undo(apps: list[App], opt: Options, everything: bool) -> int:
    ctx = _context(opt)
    for app in apps:
        heading(app.title)
        ctx.app = app.id
        for step in app.undo_steps():
            step.undo(ctx)
        Line.forget_others(ctx, [])
    if everything:
        heading("themes")
        _root().undo(ctx)
    if opt.dry_run:
        if ctx.ledger.created:
            say(
                "-",
                PINK,
                f"what install created, once it's empty {DIM}({system.display(ctx.ledger.file)}){RESET}",
            )
    else:
        for path in ctx.ledger.tidy():
            say("-", PINK, f"{system.display(path)} {DIM}(empty, created by install){RESET}")
    _done(opt)
    return 0


def status(app: App) -> tuple[str, str]:
    """(state, detail) for doctor: whether the app is hooked up to these themes, and at which level.
    A config themed by hand counts as not hooked up."""
    if not app.supported():
        return "n/a", "not on this system"
    if not app.present():
        return "no app", "not found"
    ctx = Context(Ledger(), dry_run=True)
    if any(step.stale(ctx) for step in app.steps()):
        return "stale", f"the palette changed since: nocturne install {app.id}"
    checks = {level: [c for s in tier.steps() if (c := s.check(ctx)) is not None] for level, tier in app.tiers.items()}
    if (top := _top(checks)) is not None:
        manual = any(s.manual for s in app.steps(top))
        return "hooked up", f"{top}{', and a manual step' if manual else ''}"
    if not any(checks.values()):
        return "manual", f"see: nocturne install {app.id}"
    return ("partly", "") if any(any(c) for c in checks.values()) else ("not hooked up", "")


def _top(checks: dict[Level, list[bool]]) -> Level | None:
    """The highest level whose steps, and those of every level below, are all in place."""
    top: Level | None = None
    for level in sorted(checks):  # levels with nothing to check (only notes) prove nothing either way
        if checks[level] and not all(checks[level]):
            break
        top = level if checks[level] else top
    return top
