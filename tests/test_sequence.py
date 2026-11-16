import pytest

from sentinela.sequence import GestureSequence, Status


def test_sequence_requires_time_and_neutral_between_events():
    state = GestureSequence(("paz", "rock"), hold_seconds=0.5, release_seconds=0.25)
    assert state.update(["paz"], 0) == Status.PENDING
    state.tick(0.25)  # deadline checks must not reset the camera observation
    state.update(["paz"], 0.5)
    assert state.progress == 1
    state.update(["rock"], 1)
    state.update(["rock"], 2)
    assert state.progress == 1
    state.update([], 2.1)
    state.update([], 2.4)
    state.update(["rock"], 2.5)
    assert state.update(["rock"], 3) == Status.ACCEPTED


def test_single_frame_all_classes_never_accepts():
    state = GestureSequence()
    for now in (0, 1, 2, 3):
        assert state.update(list(state.expected), now) == Status.PENDING
    assert state.progress == 0


def test_duplicate_boxes_are_ambiguous_and_reset_candidate():
    state = GestureSequence(("paz",))
    state.update(["paz"], 0)
    state.update(["paz", "paz"], 0.5)
    state.update(["paz"], 1)
    assert state.update(["paz"], 1.3) == Status.PENDING
    assert state.update(["paz"], 1.7) == Status.ACCEPTED


def test_repeated_symbols_require_release():
    state = GestureSequence(("paz", "paz"), hold_seconds=0.5, release_seconds=0.25)
    state.update(["paz"], 0)
    state.update(["paz"], 0.5)
    state.update(["paz"], 2)
    assert state.progress == 1
    state.update([], 3)
    state.update([], 3.5)
    state.update(["paz"], 4)
    assert state.update(["paz"], 4.5) == Status.ACCEPTED


def test_wrong_extra_repeated_event_is_rejected_after_release():
    state = GestureSequence(("paz", "rock"), hold_seconds=0.5)
    state.update(["paz"], 0)
    state.update(["paz"], 0.5)
    state.update([], 1)
    state.update([], 1.5)
    state.update(["paz"], 2)
    assert state.update(["paz"], 2.5) == Status.REJECTED
    assert state.update(["rock"], 3) == Status.REJECTED


def test_no_detections_and_ambiguity_time_out():
    state = GestureSequence(timeout_seconds=2)
    state.update([], 0)
    state.update(["paz", "rock"], 1)
    assert state.tick(2) == Status.TIMED_OUT


def test_unstable_or_unknown_gesture_does_not_count():
    state = GestureSequence(("paz",))
    for labels, now in [(["paz"], 0), ([], 0.5), (["unknown"], 1), (["paz"], 1.1)]:
        state.update(labels, now)
    assert state.progress == 0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"expected": ()},
        {"expected": ("unknown",)},
        {"hold_seconds": 0},
        {"release_seconds": -1},
        {"timeout_seconds": float("nan")},
    ],
)
def test_invalid_configuration(kwargs):
    with pytest.raises(ValueError):
        GestureSequence(**kwargs)


def test_monotonic_clock_required():
    state = GestureSequence()
    state.tick(2)
    with pytest.raises(ValueError):
        state.tick(1)
