# Dataset and evaluation workflow

The original data is unavailable in this repository. Do not infer permission to collect or redistribute personal images. Maintain a dataset version, provenance, annotation instructions and consent/terms outside public Git when data is private. Do not upload datasets in bug reports.

## Supported inventory validation and folds

Prepare a CSV with exactly these columns; paths are relative to the CSV (absolute paths are also accepted):

```csv
image,label,group
images/paz_01.jpeg,labels/paz_01.txt,subject-a
images/rock_01.jpg,labels/rock_01.txt,subject-b
```

Use a stable subject ID as the group when measuring unseen-person performance. At minimum, all frames from a recording session and every derivative of an original must share a group. Linking multiple sessions from the same person is necessary when evaluating unseen people. More groups are needed than the two illustrative rows above to produce five folds.

Labels use `class_id x_center y_center width height`, normalized to image dimensions. Supported classes follow the checkpoint mapping: `0 joinha`, `1 paz`, `2 saudacao_vulcana`, `3 rock`. Empty label files explicitly represent background images. Missing labels, duplicate image paths, malformed/out-of-bounds boxes, and byte-identical images placed in different groups fail validation. Image hashes do not detect visually similar frames; this tool checks existence/content, not whether image bytes decode or labels are semantically correct.

```sh
uv run --locked sentinela-split /path/to/inventory.csv /path/to/folds.json --folds 5 --seed 0
```

The command sorts the inventory, shuffles the unique group IDs with a local seeded generator and assigns groups round-robin. Every image appears in validation exactly once and never shares a group with training within its fold, including when counts are not divisible by five. It requires at least one independent group per fold. It balances **group count**, not class/image counts; inspect class coverage and group sizes before training. It is not a stratification optimizer. The JSON contains absolute paths, hashes, seed and class names. Regenerate after relocating data; inventory hashes are sensitive to CSV row ordering even though membership is not. Output files must not already exist.

## Training and evaluation still to implement

`examples/data.yaml` is a schema example, not a bundled dataset. The fold JSON is an auditable manifest, not a file accepted directly by Ultralytics. A follow-up pipeline must materialize/validate images and label layout, generate fold YAML, decode images, verify class coverage, and fail before training if files are missing or hashes changed.

Split original groups before augmentation. Geometry changes must update boxes; zoom/rotation cannot safely reuse original boxes. The legacy custom blur is random convolution, not Gaussian blur, and must not be reused. Keep naming mappings and source IDs with all derivatives.

Use held-out `model.val` detection metrics (including IoU-based mAP50–95), per-class precision/recall and confusion analysis. The legacy class-set equality score ignores localization and counts. Report fold mean/spread and sample/group counts; reserve an independent test set for final evaluation rather than reporting the winning validation fold as generalization. Record model/code/data hashes, preprocessing, thresholds, environment and seeds. Compare grayscale models only under a declared and consistent preprocessing policy. Add event-level false positives and timing/latency measurements for the webcam demo.
