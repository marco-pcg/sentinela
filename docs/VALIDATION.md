# Foundation validation

Recorded on 16 November 2026 for the project-foundation change. These results describe core code and dependency checks; they do not establish model or hardware performance.

| Check | Result |
|---|---|
| Locked core/development install, Python 3.11.15 | Passed |
| Locked core/development install, Python 3.12.13 | Passed |
| Locked core/development install, Python 3.13.14 | Passed |
| Regression suite | 40 tests passed on each Python version |
| Ruff lint / format | Passed |
| Sdist and code-only wheel build | Passed with locked build backend, without isolation |
| CLI help without ML imports | Passed |
| Core/development lock vulnerability audit | No known vulnerabilities reported by pip-audit |
| Optional runtime lock vulnerability audit | No known vulnerabilities reported by pip-audit; ML packages not installed |

The suite covers temporal dwell/release and repeats, multi-box ambiguity, wrong events, deadlines, invalid options, import safety, model checksum/load errors, camera failures/quit/cleanup, adapter integration and deterministic group fold coverage for 114 samples, plus annotation validation and refusal to overwrite manifests.

Audits query current advisory data and are a point-in-time check, not a guarantee of safety. Runtime exports are audited with pinned dependencies without resolving/installing them again. Only the native environment's applicable platform markers are audited locally; other platform runtime combinations need separate verification.

No real webcam/GUI session, checkpoint deserialization/inference, GPU test, training run or independent dataset benchmark was performed. These are tracked in issues #2–#6. Licensing and release criteria remain open in #1 and #7. Historical notebook output is not counted as new validation.
