# Contributing

Issues and discussions in English or Portuguese are welcome. Start with the roadmap and an existing issue, or open a small, concrete proposal before a major change. Include reproduction steps, expected behavior and environment versions in bug reports. Never upload private camera frames, personal datasets, credentials or untrusted model files.

Licensing is being clarified with the upstream rights holders (see NOTICE.md). Do not assume the existing code or checkpoint may be relicensed. Until that is resolved, avoid contributions containing new third-party assets or unclear rights, and do not publish packages or model derivatives on behalf of the project.

## Setup and checks

Use Python 3.11–3.13 and uv:

```sh
uv sync --locked
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pytest
uv run --locked python -m build --no-isolation
```

Create a topic branch and a focused pull request referencing its issue. Explain the observable change, validation performed, and any remaining limitations. Tests should cover behavior and regressions; core tests must run without a webcam, GPU, checkpoint deserialization or private Drive data. For camera changes, document a manual smoke test on your actual OS/device separately. The legacy notebooks are historical references, not a replacement for tested modules.

Keep reusable logic in `sentinela/`; avoid side effects on import. Add CLI options rather than machine-specific paths. Data transformations must preserve bounding boxes and source-group identity. Never split augmented derivatives independently from their original images.

## Dependency updates

Change declared dependencies in `pyproject.toml`, run `uv lock`, and review `uv.lock`. Use the commands in `.github/workflows/ci.yml` to export/audit both core and runtime environments. Audit failures need investigation, not blanket suppressions. The runtime is optional so ordinary development does not download large GPU libraries.

## Community expectations

Be respectful, assume good intent, explain technical disagreements with evidence, and credit contributors. Harassment and disclosure of personal information are not acceptable. Maintainers may edit/remove harmful content and close disruptive discussions. Use the private security route in SECURITY.md for vulnerabilities rather than a public issue containing exploit details or sensitive information.
