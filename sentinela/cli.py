"""Webcam adapter and CLI. Optional ML dependencies are imported only at run time."""

import argparse
import hashlib
import hmac
import sys
import time
from pathlib import Path

from sentinela.sequence import DEFAULT_SEQUENCE, GESTURES, GestureSequence, Status

BUNDLED_SHA256 = "71cc5c627a70e960ec85ec26e48bf4431d0d23415255c5d0a6c1b9af8fff842e"
DEFAULT_MODEL = Path(__file__).resolve().parent.parent / "TheChosenOne.pt"


def verify_model(path: Path, expected_digest: str) -> None:
    if len(expected_digest) != 64 or any(c not in "0123456789abcdef" for c in expected_digest):
        raise ValueError("Model SHA-256 must be 64 lowercase hexadecimal characters")
    with path.open("rb") as model_file:
        actual = hashlib.file_digest(model_file, "sha256").hexdigest()
    if not hmac.compare_digest(actual, expected_digest):
        raise ValueError(
            "Model checksum mismatch; obtain the expected digest from a trusted source"
        )


def run_camera(args: argparse.Namespace, cv2, model, clock=time.monotonic) -> int:
    """Return 0 for completion, 1 for rejection/timeout, 2 for errors, 130 for quit."""
    names = set(model.names.values())
    if names != GESTURES:
        raise ValueError("Model class names do not match the four supported gestures")
    state = GestureSequence(
        tuple(args.sequence), args.hold_seconds, args.release_seconds, args.timeout
    )
    cap = None
    try:
        cap = cv2.VideoCapture(args.camera)
        if not cap.isOpened():
            raise RuntimeError("Cannot open camera; check permissions and --camera")
        state.tick(clock())
        print("Gesture demo. Hold one gesture, then remove your hand between steps. q quits.")
        while state.status == Status.PENDING:
            # Check the attempt deadline before starting another capture/inference call.
            state.tick(clock())
            if state.status != Status.PENDING:
                break
            ok, frame = cap.read()
            if not ok:
                raise RuntimeError("Camera stopped delivering frames")
            kwargs = {"save": False, "conf": args.confidence, "verbose": False}
            if args.device is not None:
                kwargs["device"] = args.device
            result = model.predict(frame, **kwargs)[0]
            labels = [model.names[int(box.cls.item())] for box in result.boxes]
            state.update(labels, clock())
            display = result.plot()
            cv2.putText(
                display,
                f"Steps: {state.progress}/{len(state.expected)} | q: quit",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )
            cv2.imshow("Sentinela gesture demo", display)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("Demo cancelled.")
                return 130
        print(
            {
                Status.ACCEPTED: "Gesture sequence completed (demo only).",
                Status.REJECTED: "Wrong gesture; restart the command to try again.",
                Status.TIMED_OUT: "Attempt timed out; restart the command to try again.",
            }[state.status]
        )
        return 0 if state.status == Status.ACCEPTED else 1
    finally:
        try:
            if cap is not None:
                cap.release()
        finally:
            cv2.destroyAllWindows()


def positive(value: str) -> float:
    from math import isfinite

    number = float(value)
    if not isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("must be finite and positive")
    return number


def camera_index(value: str) -> int:
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("camera index must be nonnegative")
    return number


def confidence(value: str) -> float:
    number = positive(value)
    if number > 1:
        raise argparse.ArgumentTypeError("confidence must be in (0, 1]")
    return number


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Local gesture sequence demo; not authentication")
    result.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    result.add_argument("--model-sha256", default=BUNDLED_SHA256)
    result.add_argument("--camera", type=camera_index, default=0)
    result.add_argument("--confidence", type=confidence, default=0.5)
    result.add_argument("--device", help="Ultralytics device, e.g. cpu or 0")
    result.add_argument("--sequence", nargs="+", choices=sorted(GESTURES), default=DEFAULT_SEQUENCE)
    result.add_argument("--hold-seconds", type=positive, default=0.6)
    result.add_argument("--release-seconds", type=positive, default=0.3)
    result.add_argument("--timeout", type=positive, default=30.0)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        verify_model(args.model, args.model_sha256)
        import cv2
        from ultralytics import YOLO

        model = YOLO(str(args.model), task="detect")
        return run_camera(args, cv2, model)
    except KeyboardInterrupt:
        print("Demo cancelled.", file=sys.stderr)
        return 130
    # The CLI boundary also reports framework-specific errors (e.g. cv2.error).
    except Exception as error:
        print(f"Sentinela: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
