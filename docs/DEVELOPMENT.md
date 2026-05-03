# Development

## Setup

```bash
python -m pip install -e .
python -m pip install ruff
```

## Local quality checks

Run these before opening a PR:

```bash
ruff check .
python -m compileall src tests
python -m unittest discover -s tests -v
```

## CI

GitHub Actions workflow `.github/workflows/ci.yml` runs on push and pull requests for:
- macOS
- Windows
- Ubuntu

Each run performs:
- ruff lint
- editable install
- source/test compilation
- unit tests
- CLI help smoke test

## Packaging

Manual workflow `.github/workflows/release-package.yml` builds and uploads:
- source distribution (`sdist`)
- wheel (`.whl`)

Trigger it from the Actions tab when preparing a release candidate.
