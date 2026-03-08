# Screenlight

Screenlight is a small CLI utility that simulates a ring light for video calls by drawing a bright white border around your primary screen.

## MVP scope
- Windows + macOS support
- Primary monitor only
- Persistent defaults for border width + brightness
- Update running overlay by re-running the command

## Install

```bash
python -m pip install -e .
```

After install, the `screenlight` command is available in your shell.

On macOS, Screenlight uses a native AppKit backend via PyObjC.

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

## Notes
- `Esc` also closes the overlay window.
- If platform requirements are missing (for example PyObjC on macOS), Screenlight exits with an informative error.

## Planned next steps
- Multi-monitor support
- Improved cross-platform transparency behavior
- Optional click-through mode for border area

## License
MIT. See [LICENSE](LICENSE).
