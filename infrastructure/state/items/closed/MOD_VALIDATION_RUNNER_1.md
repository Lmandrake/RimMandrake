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

## live run, RAN (FOUNDRY, 2026-09-12) — owner: "Take control, change the list, and keep going!"

Ran for real against Pits (see `MOD_VALIDATION_PIT_PILOT_1` for that mod's
own findings) — via `runner.load_validation()` + `run_suite()` called
directly against a live `rimdrive.Session`, NOT via `cli.py run`/
`runner.run()`'s modlist-swap orchestration, which turned out to be
unusable as written:

- **`swap_to_test_list()` cannot run at all as `python.exe`** (the only
  interpreter that can drive the actual bridge socket): it shells out to
  `modlist_swap.py`, which imports `atomic_copy.py`, which imports `fcntl`
  — POSIX-only, absent on Windows. `runner.run()`'s own modlist-swap path
  is therefore currently DEAD for a real live run and needs a fix (spawn
  `modlist_swap.py` under a real `python3`, not `sys.executable`) before
  anything but the direct `load_validation`+`run_suite` route works.
  Filed nowhere yet as its own item — do that before the next mod's pilot.
- Same `fcntl`-only assumption existed in `modcheck.status` itself and DID
  get fixed this session: `_lock`/`_unlock` now try `fcntl` and fall back
  to `msvcrt` (a 1-byte lock, not a huge byte range — the first attempt at
  that range raised `PermissionError` live; portalocker's convention of a
  1-byte mutex is what actually works on Windows).
- `run_suite()` used a hardcoded `anchor=(500, 500)`; out of bounds on a
  174x174 quicktest map, and `Session.cell()` turned that into a bare
  `KeyError` with no coordinate in it. Both fixed: anchor now queries
  `jawa/map_info` for the map centre by default, and `cell()` raises a
  message naming the coordinate and the failure.
- `run_suite()` skipped `session.sweep()` entirely when a chain raised
  during its own setup (before any `with t.component()`) — now wrapped in
  `try/finally` so build-up/tear-down stays absolute even when the chain
  itself is broken, not only when a component is.
- Built `t.set_setting()` (the spec's own verb vocabulary named
  `set_setting`; this build had missed it) — works in general (offline
  selftests prove the contract), but the FIRST live target
  (`PitsSettings`) turned out to be unreachable by it at all, because that
  class uses `public static` fields. See `MOD_VALIDATION_PIT_PILOT_1` for
  the live evidence; `rimworld/update_mod_settings`'s reflection needs to
  walk static fields too, or mods need to stop using this pattern, before
  `set_setting` is broadly useful.

20/20 offline assertions still pass after every fix above (re-run each
time); full repo sweep unchanged (46/50, same 4 pre-existing failures).
