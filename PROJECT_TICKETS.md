# Screenlight Project Tickets

## Goal
Build a lightweight command-line app (`screenlight`) that simulates a ring light by displaying a bright border around the primary screen, with persisted defaults for border width and brightness.

## Confirmed Product Decisions
- MVP platform target: Windows (with cross-platform-friendly structure for future work)
- Width setting: presets (`small`, `medium`, `large`) instead of pixels
- Brightness setting: integer scale `1-10`
- Display scope: primary monitor only in v1
- UX: include short fade-in/fade-out if low complexity
- CLI flags: support both short and long options

## Ticket Backlog

### T1: Repository Bootstrap
Status: Done
- Initialize git repository
- Add `.gitignore` for Python artifacts
- Add `README.md`
- Add `LICENSE` (MIT)

### T2: CLI Spec + Argument Model
Status: Done
- Implement `screenlight --width {small,medium,large}` and `--brightness 1-10`
- Implement short flags `-w` and `-b`
- Implement `screenlight --off`
- Validate argument ranges and show clear errors

### T3: Persistent Config
Status: Done
- Save last-used values to JSON config
- Load config on each invocation
- Allow partial updates while retaining omitted values

### T4: Overlay Engine (Windows MVP)
Status: Done
- Render fullscreen always-on-top overlay
- Draw white border with transparent center
- Apply brightness via alpha mapping
- Add lightweight fade-in/fade-out animation

### T5: Single-Instance + Control Channel
Status: Done
- Maintain one active overlay instance
- Re-running command updates running overlay
- `--off` shuts down running overlay

### T6: Packaging + Entry Point
Status: Done
- Create package metadata (`pyproject.toml`)
- Expose `screenlight` console entry point
- Document editable install workflow

### T7: Validation + Hardening
Status: In Progress
- Run manual flow checks:
  - start with explicit values
  - update brightness only
  - update width only
  - turn off
- Note known limits and future enhancements

## Definition of Done (v1)
- `screenlight` starts border overlay
- `--width` and `--brightness` are independently adjustable
- Last settings persist and become defaults
- `--off` closes overlay cleanly
- Repo includes standard OSS baseline files
