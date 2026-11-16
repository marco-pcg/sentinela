# Architecture

`detect.py` is a compatibility wrapper for `sentinela.cli:main`. Importing either is safe: optional ML imports and hardware acquisition occur only inside the runtime command.

```text
CLI → checksum verification → YOLO load → camera lifetime (try/finally)
                                      ↓
frame → detector boxes → temporal state machine → demo result
                 ↘ annotated display + quit key
```

- `sequence.py`: deterministic temporal logic with injected monotonic timestamps; single-box dwell, neutral release, repeat support, wrong-event rejection and an attempt deadline.
- `cli.py`: validates configuration and model names, loads the model before opening the camera, and guarantees release/window cleanup when leaving the camera session. It never prints the configured sequence or detected symbols. It reports progress, result and operational failures.
- `data.py`: validates image/label inventory and normalized YOLO boxes; writes deterministic group-disjoint fold manifests with hashes, without overwriting existing files.
- `tests/`: pure state-machine and data tests, plus mocked camera failure/quit tests. No model deserialization or hardware dependency.

Core installation has no third-party runtime dependencies. `runtime` is an optional dependency set with an exact resolution in `uv.lock`; `dev` supplies tests, lint, packaging and audit tools. Notebook dependencies are intentionally not claimed as supported while the notebook workflow is being replaced.

## Temporal contract

Only exactly one supported detection held for the dwell interval can create an event. No detections reset an unfinished candidate. Multiple boxes, including duplicate-class boxes, reset the candidate and never count as neutral release. After an accepted event, a continuous no-detection interval is required before another event. A wrong stable event after release rejects the attempt. Terminal states cannot recover; start a new command to retry.

The timer starts when the camera opens and is checked between operations. A blocked camera read or model call cannot be interrupted by this synchronous implementation. No liveness, identity verification, brute-force protection or external authorization is provided.

## Deliberate boundaries

The notebooks are preserved for historical provenance and remain unsupported. Full box-aware augmentation, training and held-out detector evaluation are follow-up issues. No web service, database, microservice layer or auto-deployment is needed for this local demo. Hardware/model smoke validation must be recorded before claiming runtime compatibility or publishing a release.
