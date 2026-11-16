# Sentinela — technical review

Historical baseline review, recorded before the project-foundation implementation. See ROADMAP.md for completed foundation work and outstanding issues; findings describe the upstream revision below.

Review date: 16 November 2026. Repository: [noemicho/sentinela](https://github.com/noemicho/sentinela).

Reviewed `main` at commit [`81b19f0619d9327ad1341c231a4a53ca5889d4fe`](https://github.com/noemicho/sentinela/tree/81b19f0619d9327ad1341c231a4a53ca5889d4fe), dated 17 January 2025. All source references below refer to that immutable snapshot. Notebook cell numbers are zero-based JSON cell indices, including Markdown cells.

## Assessment

Sentinela is an understandable research prototype for four-class hand-gesture detection. Its small YOLOv8n-based runtime is easy to inspect, and committed notebook outputs retain useful experiment history. It is not ready to serve as an authentication mechanism or a reproducible ML release. The highest priorities are correcting temporal gesture recognition, establishing reproducible data and evaluation, and adding basic automated verification.

No repository files were modified. A shallow clone was inspected in `/tmp/sentinela-review`; this report is outside that clone. Every tracked text file and all nine notebooks' source cells were reviewed. Saved outputs were inspected for environment, training and evaluation evidence. The checkpoint was examined as ZIP/pickle instructions without deserialization. Four runtime probes executed the unchanged script with in-memory OpenCV/YOLO substitutes, without a camera, network calls, dependency installation or model execution.

No real inference, training, latency benchmark, full dependency vulnerability scan or dataset inspection was possible within this review: data, annotations and dataset YAML are absent. GitHub Actions and Releases pages could not be fetched, so hosted run history, branch protections, repository secrets, external CI and deployment settings remain unverified. Findings about missing automation refer to the tracked snapshot. This was a current-tree review, not a full Git-history secrets audit.

## Architecture and inventory

The runtime is one top-level script:

`webcam → OpenCV BGR frame → YOLO prediction (confidence 0.5) → model class names → list of unique classes → exact password comparison → console message`

OpenCV also displays annotated frames and handles the quit key. There is no server, API, database, identity store or actual access-control integration in the reviewed code. “Access granted” is a printed result.

The offline workflow is distributed across Colab notebooks and private Google Drive directories:

`original images → rename/augmentation/grayscale → fold manifests → manual image/label organization + external data.yaml → YOLOv8n training → metric plots/class-set scoring → manually selected TheChosenOne.pt`

| File or area | Responsibility | Assessment |
|---|---|---|
| `detect.py` | Camera, inference, sequence and UI | All concerns execute on import; no CLI/config boundary |
| `logica_senha.ipynb` | Earlier copy of runtime | Duplicates sequence and cleanup defects |
| `TratamentoDeDados/Renomeador.ipynb` | Re-encode and rename images | Unordered enumeration; no label mapping export |
| `TratamentoDeDados/data_augmentation.ipynb` | Zoom, rotation, channel shift, custom blur | Box transformations absent; blur implementation incorrect |
| `TratamentoDeDados/GrayScaler.ipynb` | Grayscale conversion | Drive mount appears after processing in document order |
| `Treinamento/SeparadorTrainValidation.ipynb` | Five fold manifests | Remainder and ordering defects; directories initially empty |
| `Treinamento/Treinamento_Datasets.ipynb` | Select fold, repair paths, train, copy data | Training precedes copying in document order |
| `Treinamento/treinamento_do_modelo.ipynb` | Earlier training variant | Duplicate path-repair/copy code; same ordering problem |
| `Treinamento/treinamento_modelo_noemi_teste.ipynb` | Alternate training | Simpler flow, still external paths/data |
| `Teste/PlotMetricas.ipynb` | Plot logs and compare models | Manual experiment notebook, not an automated test suite |
| `requirements.txt` | Runtime dependencies | Only two unbounded package names |
| `README.md` | Brief Portuguese project/run description | Dataset and training overview, limited reproducibility guidance |
| `TheChosenOne.pt` | Serialized trained model | About 6 MB, embedded training metadata, no release manifest |

This scale does not call for microservices. A small Python package with separate camera adapter, detector adapter, pure sequence state machine, configuration/CLI, and offline data/train/evaluate entry points would provide sufficient boundaries. Notebooks can remain thin exploration/reporting clients of those functions.

## Prioritized findings

Priority meanings: P1 = resolve before trusted use or credible model release; P2 = resolve for a reliable maintained application; P3 = maintenance improvement. Security impact is conditional on deployment; no remote service or deployed breach was established.

### F1 — P1: Sequence recognition accepts detections without temporal sequence evidence

Evidence: [`detect.py:27–42`](https://github.com/noemicho/sentinela/blob/81b19f0619d9327ad1341c231a4a53ca5889d4fe/detect.py#L27), duplicated in `logica_senha.ipynb`, cell 5.

Every detected box is appended if its class has never appeared. This records the order of first-seen distinct classes, not the sequence of gesture events. The isolated execution accepted all of the following:

- Four successive frames: `paz → rock → joinha → saudacao_vulcana`.
- A single frame with those four classes returned in that box order.
- Five frames: `paz → rock → paz → joinha → saudacao_vulcana`.

The final case silently ignores an extra gesture. Repeated symbols in a configured password can never be recorded. Multiple boxes in one frame also make password order depend on detector output ordering. A transient false positive becomes permanent, with no correction/reset and no timeout while the camera continues delivering frames.

Recommendation: define a temporal state machine. Accept one unambiguous gesture after a configurable stable interval, require release/neutral before another event, advance the expected sequence explicitly, and reject/reset on a wrong event. Add attempt duration and retry controls. Specify multi-hand behavior and validate supported class names. Acceptance tests must cover repeats, extra gestures, sustained gestures, ambiguous frames, no detections, and timeout. Confidence tuning alone does not fix this defect.

### F2 — P1 if used for authentication: The gesture password has no adequate security boundary

Evidence: [`detect.py:6`](https://github.com/noemicho/sentinela/blob/81b19f0619d9327ad1341c231a4a53ca5889d4fe/detect.py#L6), lines 40–42 and 59–66.

The password is public and hard-coded; recognized symbols and the final sequence are printed. There is no user binding, liveness or replay defense. A photograph/video or another person's gestures are plausible spoof inputs, but spoof success was not measured. With exactly these four distinct symbols, the current mechanism admits only 24 full permutations, and exposes the chosen one in source. A larger configurable alphabet alone would not establish identity or replay resistance.

Recommendation: explicitly position this as a gesture demo unless a threat model and separate trusted authentication/authorization boundary are implemented. If used as an additional interaction factor, keep credential handling outside the detector, remove secret-bearing logs, and assess presentation attacks, false accepts and false rejects. Current console output does not protect any resource.

### F3 — P1: Training and evaluation cannot be reproduced from the repository

Evidence: `Treinamento/Treinamento_Datasets.ipynb`, cells 3–5; other training notebooks; `README.md`.

Images, annotations, `data.yaml`, dataset version, split manifests and standalone experiment result files are not tracked or available through documented retrieval. Paths depend on a contributor's Drive. Multiple training variants and manually selected result paths lack an experiment registry. Saved notebook outputs are historical evidence, not a clean rerun.

Recommendation: provide a dataset schema and YAML template, explicit class mapping, lawful retrieval instructions or a synthetic smoke-test fixture, content hashes, frozen split manifests, training configuration and environment lock. Record code revision, dataset/split hashes, seed, dependency versions and selected checkpoint checksum with each run. Private data may remain private while its structure and provenance are documented.

### F4 — P1 for evaluation integrity: Five-fold splitting omits samples and is not reproducible

Evidence: `Treinamento/SeparadorTrainValidation.ipynb`, cell 1.

The splitter uses `margin = int(size * 0.2)` and five contiguous slices of an unsorted `os.listdir()` result. For a class with 114 images, each fold validates 22 images: indices 110–113 are never validated and remain in every training fold. Classes with fewer than five samples receive no validation samples. Filesystem ordering can change membership between reruns and even between independently enumerated folds. No subject/session grouping is present; related captures could cross splits, although actual leakage cannot be proven without data.

Recommendation: create one deterministic inventory, distribute all indices using a proper stratified fold splitter, and group by subject/session/source image where applicable. Persist manifests and assert every eligible source belongs to exactly one validation fold, with train/validation disjointness. Split original sources before generating derivatives. Do not infer that augmentation leakage occurred in the published model: the visible splitter points to `SentinelaOriginais`.

### F5 — P2: The augmentation pipeline does not preserve detection annotations

Evidence: `TratamentoDeDados/data_augmentation.ipynb`, cells 2–3.

Zoom and rotation transform image geometry, but the notebook neither reads nor transforms bounding boxes. Without a separate reannotation step, generated images cannot safely reuse original YOLO labels. Such a step is not documented. The function called Gaussian blur instead convolves with newly sampled unconstrained random filters of shape `[kernel, kernel, 3, 3]`, after resizing to 128×128. This mixes channels, has no normalized Gaussian kernel, and changes image dimensions. Channel shift is also named “saturation,” obscuring the actual transform.

Recommendation: use a box-aware augmentation pipeline or documented training-time augmentation; normalize/clip transformed boxes and discard invalid ones. Use an actual Gaussian blur and preserve intended dimensions. Seed random generation and retain parent-image IDs. Visually inspect transformed images with their boxes before training.

### F6 — P2: The custom evaluation score does not measure object detection quality

Evidence: `Teste/PlotMetricas.ipynb`, cells 4–6.

The score compares sets of predicted and ground-truth class IDs. It ignores box location, IoU and object counts: an incorrectly located box with the right class can count as correct; duplicate objects collapse into one set element. Missing labels are printed and skipped, and the final chart shows raw correct counts without a denominator. Experiment paths and selected models are manually curated; the active test path uses grayscale images for all selected models.

Recommendation: use detector validation on a frozen independent test set with mAP50–95, per-class precision/recall and confusion analysis. Fail on missing labels and report sample counts, preprocessing, confidence and IoU settings. Keep class-set accuracy only as an explicitly secondary image-level metric. Report cross-validation mean and spread, rather than presenting the best fold as an unbiased generalization estimate. Preserve a held-out test set for final model selection assessment, plus sequence-level false-accept/false-reject metrics if password behavior remains in scope.

### F7 — P2: Camera and window cleanup is skipped on exceptions

Evidence: [`detect.py:15–57`](https://github.com/noemicho/sentinela/blob/81b19f0619d9327ad1341c231a4a53ca5889d4fe/detect.py#L15).

The camera opens before model loading, and cleanup is only reached after normal loop exit. A mocked model-constructor exception left both camera release and window cleanup uncalled. Prediction/display exceptions have the same structural risk. The bare plotting `except` catches unrelated errors and reports them as “NO DETECTIONS.” Camera-open failure calls `exit()` without a nonzero status.

Recommendation: validate/load the model before acquisition where practical, wrap camera lifetime in `try/finally`, and catch only errors that can be handled meaningfully. Return explicit success, denial, cancellation and operational-failure statuses. Add a `main()` guard so imports do not open hardware or execute inference.

### F8 — P2: Dependency resolution is uncontrolled and incomplete for development

Evidence: [`requirements.txt`](https://github.com/noemicho/sentinela/blob/81b19f0619d9327ad1341c231a4a53ca5889d4fe/requirements.txt); notebook `pip install ultralytics` cells.

`opencv-python` and `ultralytics` have no version bounds, lockfile or hashes. Python and CPU/CUDA compatibility are unspecified. Training/preprocessing directly import TensorFlow, NumPy, Pillow, pandas and matplotlib, but no dedicated notebook/training dependency declaration exists. Some may arrive transitively or through Colab; relying on that is not a reproducible contract.

Checkpoint metadata identifies Ultralytics 8.3.59; saved notebook runs include 8.3.58 and 8.3.61, Python 3.10.12 and Torch 2.5.1+cu121. These are historical environment clues, not a recommendation to reinstall old versions. The [PyPA advisory](https://github.com/pypa/advisory-database/blob/main/vulns/ultralytics/PYSEC-2024-154.yaml) records malicious Ultralytics releases in the 8.3.41–8.3.46 range. The inspected metadata does not identify the bundled model as produced by those versions, and there is no evidence of compromise here.

Recommendation: choose and test a maintained compatible environment, separate runtime/training/development dependencies, lock transitive versions and hashes, and run advisory auditing on that resolved environment. Record CPU/GPU installation instructions. No definitive CVE count is claimed because there is no resolved installed dependency inventory.

### F9 — P2: Model distribution lacks an explicit trust and provenance policy

Evidence: `TheChosenOne.pt`; [`detect.py:25`](https://github.com/noemicho/sentinela/blob/81b19f0619d9327ad1341c231a4a53ca5889d4fe/detect.py#L25).

Static inspection found a PyTorch ZIP archive with `best/data.pkl` and serialized Ultralytics/PyTorch model classes. This is a trust boundary, not an inert data file. [Ultralytics documents pickle-based checkpoints and restricted loading behavior](https://docs.ultralytics.com/reference/nn/tasks). Safety depends on the installed loader/version; arbitrary replacement checkpoints must not be trusted. Static inspection is not a proof the model is safe, and this review did not deserialize it.

Recommendation: publish a model manifest tied to an immutable revision, verify its checksum before loading, restrict model sources, and assess a deployment format/runtime that avoids Python object deserialization. A checksum only authenticates content when the expected checksum itself comes from a trusted source. Add model card, provenance and supported-runtime information; use a release asset or model registry if model versions grow.

### F10 — P2: Notebook order and file handling make clean execution fragile

Evidence: `GrayScaler.ipynb`, cells 2–4; `SeparadorTrainValidation.ipynb`, cells 1–2; `Treinamento_Datasets.ipynb`, cells 3–5; `treinamento_do_modelo.ipynb`, cells 3–5.

Drive mounting follows data processing in two notebooks. Training precedes image organization in two others. Saved execution counts show interactive execution differed from document order. The splitter creates empty directories and initially writes paths outside the train/val subdirectories; a later notebook repairs them. Copy helpers print missing images/labels and continue rather than fail. The label-name conversion in `Treinamento_Datasets` handles lowercase `.jpg`/`.png`, not `.jpeg`, despite earlier image filters accepting JPEG. Rename helpers depend on unordered enumeration and do not export original-to-new-name mappings, creating rerun/annotation-alignment risk.

Recommendation: make data preparation an explicit validated stage before training, mount/configure first, use `Path.stem` for labels, sort stable inventories, export rename mappings, and fail if images/labels/configuration are incomplete. Execute notebooks from a fresh kernel on a small fixture to verify order. Remove duplicate path-repair logic once manifests are correct at creation.

### F11 — P2: No automated regression suite or committed CI/CD

Evidence: complete tracked file inventory; no `.github/workflows`, test runner configuration, assertions-based test suite, packaging metadata, release automation or deployment specification.

The `Teste` folder contains plotting and experiment code, not regression tests. No committed gate catches sequence bugs, fold coverage errors or broken notebook execution. Hosted protections and external automation remain unverified.

Recommendation: start with CPU-only CI on pull requests and main: locked install, lint/static checks, pure sequence tests, synthetic dataset integrity tests, notebook syntax/order smoke checks and dependency auditing. Add a separate trusted-model inference smoke job with a small fixture; do not require a webcam or GPU for ordinary pull requests. Keep expensive training and hardware/latency benchmarks manual or scheduled. For releases, package code plus model manifest, record environment/evaluation artifacts and checksums, and require acceptance thresholds. Use minimal workflow permissions and pin third-party actions to immutable revisions. Do not add continuous deployment before a deployment target and release criteria exist.

### F12 — P3, resolve before redistribution: Documentation, licensing and usability gaps

Evidence: `README.md`, notebook Colab badges, tracked inventory and checkpoint metadata.

The README requires editing a placeholder model path in source. It lacks a supported Python/platform matrix, exact installation/run commands, troubleshooting, test instructions, metric definitions and limitations. Several Colab links point to old root-level notebook locations. There is no top-level project license, model card, contribution guide or security reporting policy. The checkpoint embeds an AGPL-3.0 license string; that does not by itself establish licensing of every project file or dataset.

Recommendation: provide a CLI with model path, camera index, confidence and device options; default model resolution relative to the package; document GUI/webcam requirements and operational errors. Choose and document source, model and dataset terms after reviewing upstream requirements and rights. [Ultralytics licensing documentation](https://docs.ultralytics.com/help/FAQ/) describes its open-source and enterprise options. Add dataset consent/provenance and intended-use limitations, especially if people appear in training images. This review does not establish that any particular consent or license was violated.

## Model evidence

Static checkpoint metadata records:

| Field | Value |
|---|---|
| SHA-256 | `71cc5c627a70e960ec85ec26e48bf4431d0d23415255c5d0a6c1b9af8fff842e` |
| Embedded date | `2025-01-11T13:36:58.129487` |
| Ultralytics version | `8.3.59` |
| Class mapping | `0: joinha`, `1: paz`, `2: saudacao_vulcana`, `3: rock` |
| Training configuration | 50 epochs, image size 640, seed 0, deterministic flag true |
| Dataset/run path | Drive `Datasets/set0/data.yaml`; `Resultados/set0/train4` |
| Embedded precision / recall | 0.97974 / 0.99195 |
| Embedded mAP50 / mAP50–95 | 0.99458 / 0.89269 |

These values are retained training metadata, not independently verified results. They do not demonstrate performance on unseen subjects, different cameras or an independent test set. The runtime correctly uses `modelo.names`, rather than assuming its password list defines numeric class IDs. Its explicit `save=False` avoids writing inference images through that prediction call; it is not a comprehensive privacy guarantee for all dependencies/settings.

## Verification results

| Check | Result | Limit |
|---|---|---|
| `detect.py` Python AST parse | Passed | Syntax only |
| All nine notebooks' Python source cells | Parsed after excluding IPython shell lines | Does not establish clean execution |
| Unchanged runtime, mocked four sequential events | Accepted | Control case; no detector measurement |
| Unchanged runtime, all classes in one frame | Accepted | Confirms temporal sequence defect |
| Unchanged runtime, extra repeated event | Accepted | Confirms deduplication defect |
| Unchanged runtime, model constructor failure | Camera/window cleanup not called | Confirms resource-lifetime defect |
| Split arithmetic for 114 samples/class | Four samples never enter validation | Actual class counts unavailable |
| Checkpoint inspection | ZIP/pickle instructions and metadata examined | No deserialization or malware-free certification |
| Clone status | Clean after inspection | Report stored separately |

No runtime dependencies were installed and no training notebook was executed. No source modifications or corrective patches were made.

## Recommended implementation order

1. **Correctness and scope:** decide demo versus authentication use; fix temporal sequence semantics, reset/timeout behavior, exception cleanup and import side effects. Add focused pure-logic regressions reproducing F1 and F7.
2. **Reproducibility:** create validated data/config entry points, correct folds and box-aware augmentation, publish manifests/schema and establish a locked supported environment. Acceptance: every original is validated exactly once across folds; no source group crosses train/validation; clean preparation succeeds on a fixture.
3. **Evidence and automation:** implement proper held-out detection evaluation and sequence metrics; publish a model card and versioned artifact manifest; add CPU CI and controlled model smoke tests. Acceptance: a fresh checkout can reproduce the smoke workflow and associate every reported result with immutable code/data/model versions.
4. **Release readiness:** add CLI documentation, explicit licensing and model trust policy; benchmark latency and resource usage on the intended webcam/device; then define release/deployment criteria. Preserve notebook experiment history as supporting evidence while moving reusable implementation into tested modules.
