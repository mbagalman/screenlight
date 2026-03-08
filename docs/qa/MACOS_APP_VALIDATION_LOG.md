# macOS Conference App Validation Log

Use this file to log visibility/usability checks with real conference apps.

## Test Session Metadata
- Date:
- Tester:
- macOS version:
- Screenlight version/commit:

## Scenarios

### Zoom Desktop App
- Scenario: In-meeting, camera on, Screenlight active
- [ ] Border remains visible
- [ ] Main call window remains usable through transparent center
- [ ] No major flicker/artifacts during updates
- [ ] `screenlight -b <n>` updates live while call is active
- [ ] `screenlight --off` cleanly removes overlay
- Notes:

### Google Meet (Browser)
- Browser/version:
- Scenario: In-meeting, camera on, Screenlight active
- [ ] Border remains visible
- [ ] Meet UI remains usable through transparent center
- [ ] No major flicker/artifacts during updates
- [ ] `screenlight -w <size>` updates live while call is active
- [ ] `screenlight --off` cleanly removes overlay
- Notes:

### Optional Additional App
- App:
- Scenario:
- [ ] Border behavior acceptable
- [ ] Usability unaffected
- [ ] Update/off behavior acceptable
- Notes:

## Summary
- Overall app compatibility: PASS / FAIL / PARTIAL
- Known caveats to document in README:
- Follow-up tickets:
