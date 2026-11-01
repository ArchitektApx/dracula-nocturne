"""Steps that aren't files: a command to run, and a note on what to do by hand."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field

from nocturne.steps.base import Context, Outcome, Step
from nocturne.style import DIM, RESET, YELLOW, say


@dataclass(frozen=True)
class Run(Step):
    """A command, run by install (and another one by undo, if it has one)."""

    argv: tuple[str, ...]
    why: str
    undo_argv: tuple[str, ...] = field(default=())

    @staticmethod
    def _run(argv: tuple[str, ...], why: str, ctx: Context) -> Outcome:
        say("$", DIM, f"{' '.join(argv)} {DIM}({why}){RESET}")
        binary = shutil.which(argv[0])
        if binary is None:
            say("!", YELLOW, f"{argv[0]} isn't on PATH, run it yourself")
            return Outcome.BLOCKED
        if not ctx.dry_run:
            done = subprocess.run([binary, *argv[1:]], check=False, capture_output=True, text=True)
            if done.returncode:
                output = (done.stderr or done.stdout).strip().splitlines()
                say("!", YELLOW, output[-1] if output else f"{argv[0]} exited with {done.returncode}")
                return Outcome.BLOCKED
        return Outcome.DONE

    def apply(self, ctx: Context) -> Outcome:
        return self._run(self.argv, self.why, ctx)

    def undo(self, ctx: Context) -> None:
        if self.undo_argv:
            self._run(self.undo_argv, "undo", ctx)


@dataclass(frozen=True)
class Note(Step):
    """Something to do by hand, usually one setting that would mean rewriting the user's own config."""

    text: str
    manual = True

    def apply(self, ctx: Context) -> Outcome:  # noqa: ARG002
        say("→", YELLOW, self.text)
        return Outcome.SKIPPED
