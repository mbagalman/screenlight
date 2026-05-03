# Screenlight

Screenlight is a small CLI utility that simulates a ring light for video calls by drawing a bright white border around your primary screen.

## Platform Support

| OS | Status | Backend |
|---|---|---|
| Windows | Supported | `tkinter` transparent fullscreen overlay |
| macOS | Supported | Native AppKit overlay via PyObjC |
| Linux | Not supported in current release | N/A |

## Current Scope
- Primary monitor only
- Persistent defaults for border width + brightness
- Re-run command to update active overlay
- `--off` to close running overlay

## Install

### Windows
```bash
python -m pip install -e .
```

### macOS
```bash
python -m pip install -e .
```

`pyobjc` is installed automatically on macOS through package metadata. If needed, you can install manually:

```bash
python -m pip install "pyobjc>=10.0"
```

After install, the `screenlight` command is available in your shell.

## Usage

Turn on (or update) Screenlight:

```bash
screenlight --width medium --brightness 8
```

Short flags are also supported:

```bash
screenlight -w large -b 10
```

Turn off:

```bash
screenlight --off
```

## Settings

### Width presets
- `small` = 24 px
- `medium` = 48 px
- `large` = 72 px

### Brightness
- Integer scale: `1` to `10`

## Persistent defaults behavior
Screenlight stores your last settings and reuses them on future runs.

Examples:

```bash
# First run sets both values
screenlight -w medium -b 6

# Later update only brightness; width stays medium
screenlight -b 9

# Later update only width; brightness stays 9
screenlight -w small
```

## Design Notes

The CLI launches a detached background process that owns the overlay window. Subsequent `screenlight` invocations don't spawn a new process — they send a JSON message over a localhost TCP socket (`127.0.0.1:45871`) to update the running overlay or shut it down.

This is single-user, single-machine by design. It's appropriate for a personal workstation but not hardened for shared/multi-tenant hosts: anything that can connect to localhost can send control messages.

## Known Limitations
- Primary monitor only (multi-monitor support not yet implemented).
- Linux is not supported in the current release.
- macOS fullscreen/Spaces behavior may vary by app configuration.

## Notes
- `Esc` also closes the overlay window.
- If platform requirements are missing, Screenlight exits with an informative error.

## Planned next steps
- Multi-monitor support
- Optional click-through mode for border area

## License
MIT. See [LICENSE](LICENSE).
