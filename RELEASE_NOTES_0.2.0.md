# Screenlight 0.2.0 Release Notes

## Summary
Version 0.2.0 adds macOS support and introduces a backend abstraction to support multiple operating systems while keeping the same CLI contract.

## Highlights
- macOS overlay backend (AppKit/PyObjC)
- Backend abstraction and platform selector
- Improved error messages for unsupported/misconfigured environments
- Expanded automated tests for config and control-message handling
- Added manual QA templates for macOS conference app validation

## Compatibility
- Supported: Windows, macOS
- Not supported: Linux

## Known limitations
- Primary monitor only
- Multi-monitor support is planned for a future release
