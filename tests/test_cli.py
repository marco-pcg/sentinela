import hashlib
import importlib
import sys
from types import SimpleNamespace

import pytest

from sentinela import cli


def test_import_and_help_do_not_import_camera_or_ml(monkeypatch):
    monkeypatch.setitem(sys.modules, "cv2", None)
    monkeypatch.setitem(sys.modules, "ultralytics", None)
    importlib.reload(cli)
    import detect

    importlib.reload(detect)
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["--help"])
    assert exit_info.value.code == 0


def test_checksum_checked_before_import_or_model_load(tmp_path, monkeypatch):
    path = tmp_path / "model.pt"
    path.write_bytes(b"not a model")
    monkeypatch.setitem(sys.modules, "ultralytics", None)
    assert cli.main(["--model", str(path)]) == 2
    cli.verify_model(path, hashlib.sha256(path.read_bytes()).hexdigest())
    with pytest.raises(ValueError):
        cli.verify_model(path, "invalid")


class Camera:
    def __init__(self, opened=True):
        self.released = False
        self.opened = opened

    def isOpened(self):
        return self.opened

    def read(self):
        return True, object()

    def release(self):
        self.released = True


class CV:
    FONT_HERSHEY_SIMPLEX = 0

    def __init__(self, camera, key=-1):
        self.camera = camera
        self.closed = False
        self.key = key

    def VideoCapture(self, _index):
        return self.camera

    def destroyAllWindows(self):
        self.closed = True

    def putText(self, *args):
        pass

    def imshow(self, *args):
        pass

    def waitKey(self, _delay):
        return self.key


def model(predict):
    return SimpleNamespace(
        names={i: label for i, label in enumerate(sorted(cli.GESTURES))}, predict=predict
    )


def test_prediction_exception_releases_camera():
    cap = Camera()
    cv = CV(cap)

    def fail(*args, **kwargs):
        raise RuntimeError("prediction failed")

    with pytest.raises(RuntimeError, match="prediction failed"):
        cli.run_camera(cli.parser().parse_args([]), cv, model(fail), clock=lambda: 0)
    assert cap.released and cv.closed


def test_camera_open_failure_cleans_up():
    cap = Camera(opened=False)
    cv = CV(cap)
    with pytest.raises(RuntimeError, match="Cannot open camera"):
        cli.run_camera(cli.parser().parse_args([]), cv, model(None))
    assert cap.released and cv.closed


def test_quit_and_model_schema_validation():
    cap = Camera()
    cv = CV(cap, ord("q"))
    result = SimpleNamespace(boxes=[], plot=lambda: object())
    assert (
        cli.run_camera(
            cli.parser().parse_args([]), cv, model(lambda *a, **kw: [result]), clock=lambda: 0
        )
        == 130
    )
    assert cap.released and cv.closed
    with pytest.raises(ValueError, match="class names"):
        cli.run_camera(cli.parser().parse_args([]), cv, SimpleNamespace(names={0: "other"}))


@pytest.mark.parametrize(
    "args",
    [
        ["--confidence", "nan"],
        ["--confidence", "1.1"],
        ["--timeout", "0"],
        ["--camera", "-1"],
        ["--hold-seconds", "inf"],
        ["--sequence", "unknown"],
    ],
)
def test_cli_rejects_invalid_options(args):
    with pytest.raises(SystemExit) as exit_info:
        cli.parser().parse_args(args)
    assert exit_info.value.code == 2


@pytest.mark.parametrize(
    ("frames", "expected_code"),
    [
        ([0, 0, None, None, 1, 1], 0),
        ([0, 0, None, None, 0, 0], 1),
    ],
)
def test_camera_adapter_accepts_timed_events_and_rejects_wrong_repeat(frames, expected_code):
    from itertools import count

    cap = Camera()
    events = iter(frames)
    cap.read = lambda: (True, next(events))
    cv = CV(cap)
    names = {0: "paz", 1: "rock", 2: "joinha", 3: "saudacao_vulcana"}
    kwargs_seen = []

    def predict(frame, **kwargs):
        kwargs_seen.append(kwargs)
        boxes = [] if frame is None else [SimpleNamespace(cls=SimpleNamespace(item=lambda: frame))]
        return [SimpleNamespace(boxes=boxes, plot=lambda: object())]

    args = cli.parser().parse_args(
        ["--sequence", "paz", "rock", "--hold-seconds", "0.5", "--device", "cpu"]
    )
    detector = SimpleNamespace(names=names, predict=predict)
    assert cli.run_camera(args, cv, detector, clock=count(step=0.5).__next__) == expected_code
    assert cap.released and cv.closed
    assert all(
        kw == {"save": False, "conf": 0.5, "verbose": False, "device": "cpu"} for kw in kwargs_seen
    )


def test_camera_timeout_and_read_failure_cleanup():
    from itertools import count

    cap = Camera()
    cv = CV(cap)
    result = SimpleNamespace(boxes=[], plot=lambda: object())
    args = cli.parser().parse_args(["--timeout", "2"])
    assert (
        cli.run_camera(args, cv, model(lambda *a, **kw: [result]), clock=count(step=0.5).__next__)
        == 1
    )
    assert cap.released and cv.closed
    cap = Camera()
    cap.read = lambda: (False, None)
    cv = CV(cap)
    with pytest.raises(RuntimeError, match="stopped delivering"):
        cli.run_camera(args, cv, model(None))
    assert cap.released and cv.closed


def test_model_load_failure_never_acquires_camera(monkeypatch, tmp_path):
    path = tmp_path / "trusted-fixture.pt"
    path.write_bytes(b"fixture")
    cap = Camera()
    cv = CV(cap)
    acquired = []
    cv.VideoCapture = lambda index: acquired.append(index)

    def fail(*args, **kwargs):
        raise RuntimeError("model load failure")

    monkeypatch.setitem(sys.modules, "cv2", cv)
    monkeypatch.setitem(sys.modules, "ultralytics", SimpleNamespace(YOLO=fail))
    assert (
        cli.main(
            ["--model", str(path), "--model-sha256", hashlib.sha256(path.read_bytes()).hexdigest()]
        )
        == 2
    )
    assert acquired == []
