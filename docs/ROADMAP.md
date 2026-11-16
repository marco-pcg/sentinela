# Roadmap

The project foundation introduces a temporal state machine, safe import boundary, camera cleanup, a CLI, checksum verification, deterministic group folds, regression tests, package metadata, CI and contribution templates. This does not resolve every finding in the technical review.

| Priority | Follow-up | Completion evidence |
|---|---|---|
| Release blocker | [Clarify source/model/dataset licensing with upstream rights holders](https://github.com/marco-pcg/sentinela/issues/1) | Documented permissions, explicit licenses and attribution; no inferred grant |
| High | [Publish reproducible dataset schema/provenance and materialize folds for training](https://github.com/marco-pcg/sentinela/issues/2) | Validated fixture, decode/hash/class checks, generated YOLO layout/YAML, clean documented run |
| High | [Replace legacy augmentation with box-aware transforms](https://github.com/marco-pcg/sentinela/issues/3) | Visual overlays, valid boxes, grouped source IDs, deterministic regression fixtures |
| High | [Implement held-out detector evaluation](https://github.com/marco-pcg/sentinela/issues/4) | mAP50–95/per-class metrics, fold mean/spread, test independence, hashed reports |
| High | [Validate real model and webcam against locked runtime](https://github.com/marco-pcg/sentinela/issues/5) | CPU smoke test, actual camera/GUI cleanup, latency and OS/Python/environment record |
| Medium | [Replace private-path notebook training with reusable CLI/config](https://github.com/marco-pcg/sentinela/issues/6) | Fresh-environment fixture run, recorded code/data/config/model hashes |
| Medium | [Define release/model artifact lifecycle](https://github.com/marco-pcg/sentinela/issues/7) | Model manifest, checksums/provenance, model compatibility policy and release checklist |

Until these are resolved, the project is an attributed research fork with improved engineering, not a production authentication system or fully licensed model distribution. Issues are the place to discuss acceptance criteria and volunteer for scoped work.
