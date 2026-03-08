# macOS Manual Test Checklist

## Environment
- Date:
- Tester:
- macOS version:
- Python version:
- Installation method (`pip install -e .` / other):
- PyObjC version:

## Pre-checks
- [ ] `screenlight --help` runs successfully.
- [ ] `screenlight --off` returns cleanly when nothing is running.

## Functional Flow (Primary Monitor)

### Start with explicit values
- Command: `screenlight -w medium -b 6`
- [ ] Border appears on primary monitor.
- [ ] Border center remains transparent (underlying apps visible/usable).
- [ ] Brightness visually matches medium intensity.
- [ ] No duplicate windows appear.

### Update brightness only
- Command: `screenlight -b 9`
- [ ] Existing overlay updates without spawning duplicate instance.
- [ ] Width remains `medium`.
- [ ] Brightness increases.

### Update width only
- Command: `screenlight -w small`
- [ ] Existing overlay updates without spawning duplicate instance.
- [ ] Brightness remains previous value (`9` from step above).
- [ ] Border width visibly changes.

### Turn off
- Command: `screenlight --off`
- [ ] Overlay fades out and closes.
- [ ] Re-running `screenlight --off` reports no running instance.

## Persistence Checks
- [ ] Run `screenlight -w large -b 4`, then `screenlight -b 7`; width remains `large`.
- [ ] Run `screenlight --off`, then `screenlight`; last saved config is restored.

## Negative / Validation Checks
- Command: `screenlight -b 11`
- [ ] Returns non-zero with clear error message.
- Command: `screenlight -w huge`
- [ ] Returns non-zero with argparse choice error.

## Stability Checks
- [ ] Rapidly run 5 updates in sequence; no crash/hang.
- [ ] `Esc` closes overlay cleanly.
- [ ] App exits cleanly after shutdown (no orphan process).

## Result Summary
- Overall result: PASS / FAIL
- Notes:
- Defects filed:
