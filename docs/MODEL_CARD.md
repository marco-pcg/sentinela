# Bundled model: TheChosenOne.pt

## Intended use and limits

Four-class local gesture detection for a webcam demonstration. Not identity verification or access control. No replay resistance, demographic/subgroup assessment, robustness certification, or independently reproduced benchmark is available. Performance can vary with lighting, skin appearance, camera, pose, background and multiple hands. No supported production deployment is claimed.

## Recorded artifact

- Original source: noemicho/sentinela, commit `81b19f0619d9327ad1341c231a4a53ca5889d4fe`.
- SHA-256: `71cc5c627a70e960ec85ec26e48bf4431d0d23415255c5d0a6c1b9af8fff842e`.
- Embedded timestamp: `2025-01-11T13:36:58.129487`.
- Embedded Ultralytics version: `8.3.59`; YOLOv8n training notebooks use 50 epochs and image size 640.
- Embedded classes: `0 joinha`, `1 paz`, `2 saudacao_vulcana`, `3 rock`.
- Embedded training config: seed 0, deterministic flag true, `Datasets/set0/data.yaml`, `Resultados/set0/train4` on a contributor's Drive.
- Embedded validation metrics: precision 0.97974, recall 0.99195, mAP50 0.99458, mAP50–95 0.89269.

These values were obtained through static ZIP/pickle-instruction inspection, without deserializing the model. They are historical metadata, not independent measurements or an assertion that a held-out test set achieved these scores. The original README describes 456 images; data and annotations are absent. We cannot reconstruct subjects, capture conditions, exact splits, consent or test-set independence.

## Trust and licensing

The checkpoint contains serialized Python/PyTorch objects. A matching checksum is necessary to detect unexpected replacement but does not prove safety. Only use trusted checkpoints and supported loaders; do not bypass restricted loading on an unknown file. Runtime compatibility with the locked dependency set still needs a documented real-model smoke test.

The checkpoint embeds an AGPL-3.0 licensing string referencing Ultralytics. Source/model/dataset terms need clarification before a public release; see NOTICE.md. Do not assume the model metadata grants rights in the original training images or all repository files.
