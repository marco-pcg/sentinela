"""Pure temporal gesture recognition, independent of detector and camera libraries."""

from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import StrEnum
from math import isfinite

GESTURES = frozenset({"paz", "rock", "joinha", "saudacao_vulcana"})
DEFAULT_SEQUENCE = ("paz", "rock", "joinha", "saudacao_vulcana")


class Status(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    TIMED_OUT = "timed_out"


@dataclass
class GestureSequence:
    """Require a stable single box, then a neutral interval between gesture events.

    Wrong stable events terminate the attempt. Multiple boxes never count as an
    event or a release. `now` is a monotonic timestamp supplied by the caller.
    """

    expected: tuple[str, ...] = DEFAULT_SEQUENCE
    hold_seconds: float = 0.6
    release_seconds: float = 0.3
    timeout_seconds: float = 30.0
    status: Status = field(default=Status.PENDING, init=False)
    progress: int = field(default=0, init=False)
    _start: float | None = field(default=None, init=False)
    _last: float | None = field(default=None, init=False)
    _candidate: str | None = field(default=None, init=False)
    _candidate_since: float | None = field(default=None, init=False)
    _waiting_release: bool = field(default=False, init=False)
    _neutral_since: float | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        self.expected = tuple(self.expected)
        if not self.expected or any(label not in GESTURES for label in self.expected):
            raise ValueError("Sequence must contain supported gestures and cannot be empty")
        for value in (self.hold_seconds, self.release_seconds, self.timeout_seconds):
            if not isfinite(value) or value <= 0:
                raise ValueError("Timing values must be finite and positive")

    def tick(self, now: float) -> Status:
        """Advance the deadline without treating elapsed time as a camera observation."""
        if not isfinite(now) or (self._last is not None and now < self._last):
            raise ValueError("Timestamps must be finite and monotonic")
        self._last = now
        if self.status != Status.PENDING:
            return self.status
        if self._start is None:
            self._start = now
        if now - self._start >= self.timeout_seconds:
            self.status = Status.TIMED_OUT
            return self.status
        return self.status

    def update(self, labels: Iterable[str], now: float) -> Status:
        if self.tick(now) != Status.PENDING:
            return self.status
        labels = tuple(labels)
        if self._waiting_release:
            if labels:
                self._neutral_since = None
            elif self._neutral_since is None:
                self._neutral_since = now
            elif now - self._neutral_since >= self.release_seconds:
                self._waiting_release = False
                self._neutral_since = None
            return self.status
        if len(labels) != 1 or labels[0] not in GESTURES:
            self._candidate = None
            self._candidate_since = None
            return self.status
        label = labels[0]
        if self._candidate != label:
            self._candidate, self._candidate_since = label, now
            return self.status
        if now - self._candidate_since < self.hold_seconds:
            return self.status
        if label != self.expected[self.progress]:
            self.status = Status.REJECTED
            return self.status
        self.progress += 1
        self._candidate = None
        self._candidate_since = None
        self._waiting_release = True
        if self.progress == len(self.expected):
            self.status = Status.ACCEPTED
        return self.status
