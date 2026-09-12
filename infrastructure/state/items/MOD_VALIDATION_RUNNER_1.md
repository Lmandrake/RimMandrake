# MOD_VALIDATION_RUNNER_1 — build modcheck, the scripted mod-functionality validator

The spec is the authority: `design/RimMandrake/mod_validation_runner_spec.md`
(owner-designed sitting 2026-09-12; every ruling in it is his, dated).

## spec
Build `src/RimMandrake/Utils/modcheck/`: the modcheck library (owner re-ruling 2026-09-12:
per-mod PYTHON scripts on a shared library, steps-YAML dropped) — extract
Session.mutate() from rimbench/core.py, add reconnect+post-condition polling,
spawn-tracking teardown with pause verification (spec §1b), verb vocabulary v1
(clear_area, spawn, spawn_pawn, walk_over, wait_ticks, set_weather,
set_setting, bridge_call, expect_* read-backs, screenshot), settings-toggle floor
enforcement (refuse a mod whose toggle has zero components), the run session
(modlist_swap to MINIMAL+mod, quicktest, bridge lock, restore FULL after),
`rimflow verify` emission, HTML sheet to `Transient/modcheck/`, auto-filed
findings on failure with run continuing, `modcheck_status.json` registry +
`declare minor` staleness flow (minor is ONLY a trivial change without gameplay
effect — text or a very slight parameter adjustment; the declare command records
the diff --stat alongside the why so the claim is checkable), and the
deploy-tool skip rule for `validation.py`. The LLM never drives: deterministic
run, evidence bundle, one judging pass at the end; --halt-on-fail for authoring.

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
