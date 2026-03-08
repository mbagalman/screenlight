# Changelog

All notable changes to this project are documented in this file.

## [0.2.0] - 2026-03-08
### Added
- Backend abstraction layer for overlay implementations.
- Windows backend module extracted from monolithic service.
- Native macOS backend using AppKit/PyObjC.
- Backend-agnostic service/control-message tests.
- Config persistence/merge test coverage.
- macOS manual QA checklist and conference app validation log templates.

### Changed
- Platform selection now explicitly routes to Windows/macOS backends.
- Unsupported platform errors are now explicit and actionable.
- README now includes OS support matrix, per-OS install notes, and known limitations.

### Notes
- macOS support requires `pyobjc>=10.0`.
- Primary monitor only in this release.
- Linux support is not included in this release.

## [0.1.0] - 2026-03-07
### Added
- Initial Screenlight MVP for Windows.
- CLI with persistent `width` and `brightness` settings.
- Single-instance update flow and `--off` shutdown command.
