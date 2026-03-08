# Development

## Local quality checks

Run these before opening a PR:

```bash
python -m compileall src tests
PYTHONPATH=src python -m unittest discover -s tests -v
```

## CI

GitHub Actions workflow `.github/workflows/ci.yml` runs on push and pull requests for:
- macOS
- Windows
- Ubuntu

Each run performs:
- editable install
- source/test compilation
- unit tests
- CLI help smoke test

## Packaging

Manual workflow `.github/workflows/release-package.yml` builds and uploads:
- source distribution (`sdist`)
- wheel (`.whl`)

Trigger it from the Actions tab when preparing a release candidate.
