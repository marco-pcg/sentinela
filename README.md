# Sentinela

Sentinela is a local webcam demo that detects four hand gestures with YOLOv8 and checks a timed sequence: **paz**, **rock**, **joinha**, and **saudacao_vulcana**. This fork builds on [noemicho/sentinela](https://github.com/noemicho/sentinela).

**This is a gesture demonstration, not an authentication system.** It does not identify a person, resist video replay, or protect a resource. Source/model/dataset licensing still needs clarification with the original rights holders; see [NOTICE.md](NOTICE.md). Public availability and a fork do not settle redistribution rights.

## Quick start

Use Python 3.11–3.13 and [uv](https://docs.astral.sh/uv/getting-started/installation/). Run from a checkout with a desktop display and webcam:

```sh
git clone https://github.com/marco-pcg/sentinela.git
cd sentinela
uv sync --locked --extra runtime
uv run --locked --extra runtime sentinela --device cpu
```

The optional runtime installs PyTorch/Ultralytics and OpenCV and can require a substantial download. GPU setup depends on your system; CPU is the documented starting point. The core and developer checks do not need ML dependencies, a GPU or a camera. The lock records resolution, not a successful hardware compatibility certification; real webcam/model smoke testing is tracked in the roadmap.

The default sequence is `paz rock joinha saudacao_vulcana`. Hold **one** gesture for at least 0.6 seconds, then remove your hand for at least 0.3 seconds before the next gesture. A stable wrong gesture rejects the attempt. Multiple detections do not count. Repeated symbols are supported after a neutral interval. Attempts time out after 30 seconds; restart the command to retry. Press **q** to cancel.

```sh
uv run --locked --extra runtime sentinela --camera 1 --confidence 0.6 --timeout 45
uv run --locked --extra runtime sentinela --sequence paz paz rock
uv run --locked --extra runtime python detect.py --help
```

Exit codes: `0` sequence completed, `1` rejected/timed out, `2` operational failure, `130` cancelled. Successful completion is a demo result, not authorization. The deadline is checked between capture/inference calls; it cannot interrupt a blocked camera driver or model call.

The bundled checkpoint is verified against its recorded SHA-256 before loading. For another trusted four-class checkpoint, supply both its path and an independently trusted checksum:

```sh
uv run --locked --extra runtime sentinela --model /path/to/model.pt --model-sha256 TRUSTED_SHA256
```

A checksum does not make an untrusted pickle model safe. Read the [model card](docs/MODEL_CARD.md). The wheel contains code only; the checkout supplies the model file. If installing the wheel separately, pass `--model` explicitly.

## Development

```sh
uv sync --locked
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pytest
uv run --locked python -m build --no-isolation
```

See [CONTRIBUTING.md](CONTRIBUTING.md), the [architecture](docs/ARCHITECTURE.md), [data workflow](docs/DATA.md), and [roadmap](docs/ROADMAP.md). CI runs core checks on Python 3.11–3.13, builds the package and audits locked dependency exports. It does not load the checkpoint or train a model. Dependencies are updated by Dependabot; regenerated locks and successful tests are required with updates.

## Data and experiments

The original README described 456 images, approximately 114 per class, 50 epochs, image size 640, and five-fold 80/20 evaluation. The original images, labels and dataset YAML are not included. We cannot independently reproduce those results yet.

The original Portuguese Colab notebooks remain in `TratamentoDeDados/`, `Treinamento/`, `Teste/`, and `logica_senha.ipynb` as historical experiment material. They depend on private Drive paths and out-of-order execution, and contain known augmentation/evaluation issues. **They are not the supported pipeline.** Do not use their class-set score as object detection accuracy or use the legacy password notebook for authentication. Follow [docs/DATA.md](docs/DATA.md) and the tracked follow-up work.

## Troubleshooting

- Camera failure: check OS camera permissions, close competing applications and try `--camera 1`.
- GUI failure: use a local graphical session and the GUI-enabled `opencv-python`; do not combine conflicting OpenCV distributions.
- Missing model: run from a full checkout or pass the model path explicitly.
- Checksum mismatch: stop and check provenance; do not simply copy the observed digest to bypass verification.
- Missing dependencies: use `uv sync --locked --extra runtime`. `pip install -r requirements.txt` is a convenience alternative, but does not use `uv.lock`.
- ML loader errors: retain the error and environment versions in a bug report; do not disable loader safeguards to force a model to load.

## Português

Demonstração local de reconhecimento dos gestos paz, rock, joinha e saudação vulcana. Segure um gesto por 0,6 s e retire a mão por 0,3 s entre etapas. Use **q** para sair. O projeto não é um sistema de autenticação. Issues e contribuições em português ou inglês são bem-vindas; consulte os documentos acima para instalação, limitações e licenciamento pendente.
