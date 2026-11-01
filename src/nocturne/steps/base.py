"""What every install step can do: apply itself, undo itself, and say whether it's in place."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from nocturne.ledger import Ledger


class Outcome(Enum):
    DONE = auto()
    BLOCKED = auto()  # something of the user's is in the way
    SKIPPED = auto()  # nothing to do here (no such shell config, a note)


@dataclass
class Context:
    ledger: Ledger
    dry_run: bool = False
    force: bool = False
    app: str = ""  # the app whose steps run


class Step(ABC):
    # a step the user does by hand: shown, never checked
    manual: ClassVar[bool] = False

    @abstractmethod
    def apply(self, ctx: Context) -> Outcome: ...

    def undo(self, ctx: Context) -> None:  # noqa: B027  # most steps have something to undo, notes don't
        """Take the step back out, leaving anything the user changed alone."""

    def check(self, ctx: Context) -> bool | None:  # noqa: ARG002
        """Whether the step is in place; None when there's nothing to check."""
        return None

    def stale(self, ctx: Context) -> bool:  # noqa: ARG002
        """In place, but from an older build (a copy, made before the palette changed)."""
        return False
