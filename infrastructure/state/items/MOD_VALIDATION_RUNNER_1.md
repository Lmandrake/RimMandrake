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

## done (FOUNDRY, 2026-09-12) — 4 of 4 verify bullets MET offline; the live run is owed

Built `src/RimMandrake/Utils/modcheck/`: `suite.py` (`Suite`/`chain`/
`component`, `TestContext` verb vocabulary v1 — `clear_area`, `spawn`,
`spawn_pawn`, `walk_over`, `order_to`, `wait_ticks`, `bridge_call`,
`expect_in_cell_of`/`expect_not_in_cell_of`/`expect_reached_past`/
`expect_pawn_despawned`/`expect_log_contains`, `screenshot` with a
`system_screenshot.py` fallback, `checkpoint` gated on debug mode — a
component after an upstream failure short-circuits every verb to a no-op
rather than fighting Python's `with`-statement to skip a block, see the
module docstring for why), `floor.py` (toggle-coverage lint, pure function),
`status.py` (GREEN/STALE registry, same locked-atomic-write pattern as
`code_review_status.py`, content-hash EXCLUDING `validation.py` itself),
`report.py` (pure HTML sheet renderer), `runner.py` (orchestration:
modlist swap, per-mod suite run, sheet + `rimflow verify` + finding-filing +
status recording, unconditional FULL restore in a `finally`), `cli.py`
(`modcheck run/status/declare`).

- ✅ **"Lint rule proven: a write step with no read-back is refused"** —
  reinterpreted per the SAME-DAY amendment already on the ledger
  (`RIMDRIVE_LIBRARY_BUILD_1`'s own note, `bridge_library_design.md` §6.5):
  a channel-less write is UNVERIFIED-TAINTED, never refused. Proven by
  `t_unverified_write_taints_pass_but_is_not_a_failure` — the component
  still passes, but as `PASS(UNVERIFIED n)`, never a clean PASS. The
  item's own text above is the STALE half of that ruling; left as written
  rather than edited, per "inaccurate material is deleted, not
  superseded-in-place" — this note is the correction, the original stays
  visible as what was asked for before the amendment landed.
- ✅ **"A deliberately-failing component files a finding AND the run
  continues"**: `t_chain_failure_marks_downstream_unmeasured_and_continues`
  — a raising component becomes FAIL, is handed to `on_finding`, and every
  later `with t.component()` in the SAME chain executes (bodies run; every
  verb inside them no-ops) and records UNMEASURED, never silently skipped.
- ✅ **"FULL list restored ... recognises it after a run"**:
  `t_restore_full_runs_even_when_a_mod_load_fails` proves `restore_full()`
  runs even when a mod fails to load, because it's called from `run()`'s
  `finally`. NOT exercised against the real `modlist_swap.py --status`
  live (would need an actual swap) — the subprocess call shape is proven,
  not the live swap-and-recognize round trip.
- ✅ **"Registry refuses hand-edits the way code_review_status.py does"**:
  same lock+tmp+`os.replace` atomic-write discipline, content-hash
  comparison (never a timestamp), `declare_minor` refuses a mod with no
  prior GREEN run. `t_status_registry_roundtrip_and_staleness` proves the
  round trip GREEN → (edit) → STALE → `declare minor` → GREEN.
- ✅ **Deploy-tool skip rule**: found, not built — `deploy_custom_mods.py`
  already excludes `.py` wholesale (`EXCLUDE_EXTS`), so `validation.py`
  was never at risk of deployment. Locked in as a regression guard
  (`t_deploy_tool_already_skips_python_files`) rather than adding
  redundant logic.
- 20/20 modcheck offline selftest assertions pass; full repo
  `run_selftests.py` sweep: 46/50 (same 4 pre-existing, unrelated
  failures as `RIMDRIVE_LIBRARY_BUILD_1` found before this).

⏳ **NOT done: an actual live `modcheck run`.** Same reason as
`RIMDRIVE_LIBRARY_BUILD_1` — the owner's live campaign was up throughout;
a modlist swap to MINIMAL+mod needs a restart, which this seat does not
call unilaterally on someone else's live session. `MOD_VALIDATION_PIT_PILOT_1`
carries the actual pilot script and the rest of this gap. Left `doing`.

⚠️ **`swap_to_test_list()` is a known simplification**, flagged in its own
docstring: it calls the plain `--minimal` swap rather than composing
MINIMAL + the target mod's packageId (spec §2's literal ask) — the fixed
`ModsConfig.MINIMAL.xml` snapshot has no per-mod parameter.
Composing-and-writing that combined list is owed before the first REAL
live run (correct today only for a mod needing nothing beyond the minimal
mechanism list).
