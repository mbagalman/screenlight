# Screenlight macOS Extension Plan + Ticket Pack

## 1) Objective
Extend Screenlight from Windows-first to support macOS while preserving the existing CLI contract:
- `screenlight -w/--width {small,medium,large}`
- `screenlight -b/--brightness 1-10`
- `screenlight --off`
- Persistent defaults and single-instance behavior

## 2) Non-Goals (for this phase)
- Multi-monitor support
- New width/brightness semantics
- GUI settings panel
- Auto-start at login

## 3) Recommended Technical Approach
Use a backend abstraction for overlays and add a macOS-native backend:
- Keep CLI and config as cross-platform shared logic.
- Split overlay into per-platform modules:
  - Windows backend (existing tkinter-based approach)
  - macOS backend (PyObjC/AppKit)
- On macOS, create a border-only transparent overlay window using `NSWindow` + `CAShapeLayer` (even-odd fill mask) so center stays transparent.
- Reuse existing local socket control channel for `update`, `off`, and `ping`.

Why this approach:
- Avoids relying on tkinter transparency behavior on macOS, which is inconsistent.
- Gives control over always-on-top level, transparency, and animation timing.
- Keeps current CLI UX unchanged.

## 4) Architecture Changes
1. Add overlay backend interface (`start`, `update`, `shutdown`).
2. Move current service orchestration (IPC, message loop) into a platform-neutral service manager.
3. Implement `windows_backend.py` from current `service.py` behavior.
4. Implement `macos_backend.py` with AppKit event loop and transparent border rendering.
5. Add backend selection by platform (`sys.platform`).

## 5) Risks + Mitigations
- Risk: macOS window layering behavior differs across Spaces/fullscreen apps.
  - Mitigation: Add targeted manual test matrix for normal desktop + fullscreen conference app.
- Risk: PyObjC dependency complexity.
  - Mitigation: make dependency conditional for Darwin only.
- Risk: race conditions around startup/IPC ping.
  - Mitigation: keep current ping handshake and add backend-ready signal before accepting updates.
- Risk: `--off` stale socket edge case.
  - Mitigation: keep robust error path and ensure socket cleanup in shutdown hooks.

## 6) Ticket Pack

### Epic M0: Foundation Refactor (Backend Abstraction)
Status: Done

#### M0-1 Create platform backend interface
- Type: Engineering
- Priority: P0
- Description: Introduce a backend protocol/class defining `run()`, `update(width, brightness)`, and `shutdown()`.
- Status: Done
- Acceptance Criteria:
  - Service code compiles with new interface.
  - Existing runtime behavior on Windows remains unchanged.

#### M0-2 Extract current tkinter behavior into Windows backend module
- Type: Engineering
- Priority: P0
- Description: Move current overlay rendering logic out of monolithic `service.py` into `windows_backend.py`.
- Status: Done
- Acceptance Criteria:
  - Windows path remains functionally identical.
  - No CLI behavior regression.

#### M0-3 Add platform selector + unsupported-platform error contract
- Type: Engineering
- Priority: P0
- Description: Add deterministic platform selection (`win32` -> windows backend, `darwin` -> mac backend, otherwise explicit unsupported message).
- Status: Done
- Acceptance Criteria:
  - Unsupported OS prints actionable message and exits non-zero.
  - Selector unit tests pass.

### Epic M1: macOS Overlay Backend
Status: Done

#### M1-1 Add conditional macOS dependency wiring
- Type: Build/Packaging
- Priority: P0
- Description: Add `pyobjc` as a Darwin-only dependency path in packaging docs/setup.
- Status: Done
- Acceptance Criteria:
  - Install instructions include macOS dependency path.
  - Windows install flow remains unaffected.

#### M1-2 Implement macOS overlay window shell
- Type: Engineering
- Priority: P0
- Description: Create borderless, topmost, transparent `NSWindow` covering primary display.
- Status: Done
- Acceptance Criteria:
  - Window appears on primary monitor only.
  - Center can remain transparent (apps visible underneath).

#### M1-3 Implement border rendering with width presets
- Type: Engineering
- Priority: P0
- Description: Render white border with `small|medium|large` mapped to pixel thickness.
- Status: Done
- Acceptance Criteria:
  - Border dimensions match preset map.
  - No center fill artifact at any preset.

#### M1-4 Implement brightness and fade animation on macOS
- Type: Engineering
- Priority: P1
- Description: Map brightness `1-10` to alpha and implement short fade-in/fade-out.
- Status: Done
- Acceptance Criteria:
  - Brightness visually changes across the scale.
  - Startup/shutdown fade duration is comparable to Windows behavior.

#### M1-5 Connect IPC update/off handling to macOS backend
- Type: Engineering
- Priority: P0
- Description: Ensure live updates and shutdown commands work against macOS backend.
- Status: Done
- Acceptance Criteria:
  - Re-running CLI updates active overlay without duplicate instances.
  - `screenlight --off` closes macOS overlay reliably.

### Epic M2: QA + Hardening
Status: In Progress

#### M2-1 Add backend-agnostic service tests
- Type: Testing
- Priority: P1
- Description: Add tests for config merge, message validation, and platform selection.
- Status: Done
- Acceptance Criteria:
  - Tests run in CI without requiring GUI.
  - Core command validation logic has coverage.

#### M2-2 Add macOS manual test checklist
- Type: QA
- Priority: P0
- Description: Create repeatable checklist for startup, update-only width/brightness changes, and `--off`.
- Status: Done
- Acceptance Criteria:
  - Checklist includes expected outcomes and failure capture fields.
  - Checklist run results are logged in PR description.

#### M2-3 Validate behavior with common conference apps
- Type: QA
- Priority: P1
- Description: Verify visibility and usability with at least two apps (for example Zoom + Google Meet in browser).
- Status: Pending manual execution
- Acceptance Criteria:
  - Documented pass/fail notes for each app scenario.
  - Any known caveats added to README.

### Epic M3: Docs + Release Prep

#### M3-1 Update README for dual-platform support
- Type: Documentation
- Priority: P0
- Description: Add OS matrix, install instructions per OS, and known limitations.
- Acceptance Criteria:
  - README clearly distinguishes Windows and macOS setup.
  - Command examples remain consistent with current CLI.

#### M3-2 Add migration notes and version bump
- Type: Release
- Priority: P1
- Description: Bump package version and note macOS support in changelog/release notes.
- Acceptance Criteria:
  - Version bump committed.
  - Release notes include macOS scope and known limitations.

## 7) Suggested Execution Order
1. M0-1, M0-2, M0-3
2. M1-1, M1-2, M1-3, M1-5
3. M1-4
4. M2-1, M2-2, M2-3
5. M3-1, M3-2

## 8) Definition of Done (macOS phase)
- macOS users can run `screenlight` with the same flags as Windows.
- Border overlay runs on primary monitor with transparent center.
- Width presets and brightness scale work and persist.
- Re-run updates active instance; `--off` shuts it down.
- README documents macOS installation and caveats.
