# MOD_VALIDATION_RUNNER_1 — build modcheck, the scripted mod-functionality validator

The spec is the authority: `design/RimMandrake/mod_validation_runner_spec.md`
(owner-designed sitting 2026-09-12; every ruling in it is his, dated).

## spec
Build `src/RimMandrake/Utils/modcheck/`: steps-file schema + parser, step
vocabulary v1 (spawn_thing, spawn_pawn, move_pawn_to, wait_ticks, set_weather,
set_setting, bridge_call, expect read-backs, screenshot), settings-toggle floor
enforcement (refuse a mod whose toggle has zero components), the run session
(modlist_swap to MINIMAL+mod, quicktest, bridge lock, restore FULL after),
`rimflow verify` emission, HTML sheet to `Transient/modcheck/`, auto-filed
findings on failure with run continuing, `modcheck_status.json` registry +
`declare minor` staleness flow, and the deploy-tool skip rule for
`validation.steps.yaml`.

## verify
- Lint rule proven: a write step with no read-back anywhere in its component is
  refused.
- A deliberately-failing component files a finding AND the run continues.
- FULL list restored and `modlist_swap.py --status` recognises it after a run.
- Registry refuses hand-edits the way code_review_status.py does.

## traps
- The ~40 silent-success bridge calls are the reason this exists — read-back
  after EVERY write, and the bridge screenshot itself can lie (fall back to
  system_screenshot.py on success-and-nothing).
- Never run during an owner session; one bridge driver.
